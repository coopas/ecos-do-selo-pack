package ecos.maquinas;

import com.gregtechceu.gtceu.api.capability.IEnergyContainer;
import com.gregtechceu.gtceu.api.capability.forge.GTCapability;
import com.simibubi.create.content.kinetics.base.DirectionalKineticBlock;
import com.simibubi.create.content.kinetics.base.KineticBlockEntity;
import ecos.maquinas.EcosMaquinas.Constantes;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.common.capabilities.Capability;
import net.minecraftforge.common.capabilities.ICapabilityProvider;
import net.minecraftforge.common.util.LazyOptional;

import java.util.List;
import java.util.Locale;

/**
 * Dínamo Cinético: consome rotação do Create (impacto da tier por RPM, registrado em BlockStressValues.IMPACTS) e gera
 * EU do GregTech: EU/t = min(voltagem, impacto * |RPM| / SU_POR_EU). Parado ou sobrecarregado gera 0; o sentido da
 * rotação não importa. O EU vai para um buffer interno de 16x a voltagem e, a cada tick, sai em pacotes de exatamente
 * 1 A na voltagem da tier (ULV 8, LV 32) para o vizinho da face de saída (a oposta ao eixo) que tenha
 * CAPABILITY_ENERGY_CONTAINER. Frações de EU/t acumulam até fechar um pacote.
 *
 * NBT: "Buffer" (EU, long) e "Resto" (fração, double). Os dois são opcionais: dínamos salvos sem eles (Task 3) carregam
 * vazios; valores adulterados são presos a 0..16x a voltagem.
 */
public class DinamoBlockEntity extends KineticBlockEntity {
    public static final int BUFFER_VOLTAGENS = 16;

    /** IEnergyContainer de saída exposto na face de saída (cabos do GregTech se ligam a ele). */
    private final Saida saida = new Saida();
    private long buffer;
    private double resto;
    private long ultimoSync = -1;

    public DinamoBlockEntity(BlockEntityType<?> type, BlockPos pos, BlockState state) {
        super(type, pos, state);
    }

    /** Tier do bloco; ULV se o estado não for de dínamo (nunca deveria acontecer). */
    public DinamoBlock.Tier getTier() {
        return m_58900_().m_60734_() instanceof DinamoBlock d ? d.tier : DinamoBlock.Tier.ULV;
    }

    public long getVoltagem() {
        return getTier().voltagem;
    }

    public long getBuffer() {
        return buffer;
    }

    public long getBufferMax() {
        return BUFFER_VOLTAGENS * getVoltagem();
    }

    /** Face do eixo (FACING); null se o estado não for de dínamo. */
    Direction eixo() {
        BlockState s = m_58900_();
        return s.m_61138_(DirectionalKineticBlock.FACING) ? s.m_61143_(DirectionalKineticBlock.FACING) : null;
    }

    /** Face por onde o EU sai: a oposta ao eixo. */
    Direction faceSaida() {
        Direction e = eixo();
        return e == null ? null : e.m_122424_();
    }

    /** EU/t gerados agora: nunca negativo, nunca acima de 1 A na voltagem da tier. */
    public double getEuT() {
        float rpm = Math.abs(getSpeed());
        if (overStressed || !Float.isFinite(rpm) || rpm <= 0) return 0;
        DinamoBlock.Tier t = getTier();
        return Math.min((double) t.voltagem, (double) t.impacto * rpm / Constantes.SU_POR_EU);
    }

    @Override
    public void tick() {
        super.tick();
        if (f_58857_ == null || f_58857_.f_46443_) return;
        long max = getBufferMax();
        double eut = getEuT();
        if (eut > 0 && buffer < max) {
            resto += eut;
            long inteiro = (long) resto;
            resto -= inteiro;
            buffer = Math.min(max, buffer + inteiro);
            m_6596_();
        }
        empurrar();
    }

    /** Um pacote de 1 A na voltagem exata da tier para o vizinho da face de saída, se houver EU para isso. */
    private void empurrar() {
        long v = getVoltagem();
        Direction face = faceSaida();
        if (buffer < v || face == null) return;
        BlockPos alvo = f_58858_.m_121945_(face);
        if (!f_58857_.m_46749_(alvo)) return;  // não carrega chunk vizinho
        BlockEntity viz = f_58857_.m_7702_(alvo);
        // O jar de compilação não tem os patches do Forge: em runtime todo BlockEntity é ICapabilityProvider.
        if (!((Object) viz instanceof ICapabilityProvider prov)) return;
        Direction lado = face.m_122424_();
        IEnergyContainer c = prov.getCapability(GTCapability.CAPABILITY_ENERGY_CONTAINER, lado).orElse(null);
        if (c == null || !c.inputsEnergy(lado)) return;
        long amperes = c.acceptEnergyFromNetwork(lado, v, 1);
        if (amperes > 0) {
            buffer -= v;  // no máximo 1 A por tick, mesmo que o vizinho diga mais
            m_6596_();
        }
    }

    @Override
    public void lazyTick() {
        super.lazyTick();
        if (f_58857_ == null || f_58857_.f_46443_) return;
        if (buffer != ultimoSync) {  // tooltip do cliente acompanha o buffer sem pacote todo tick
            ultimoSync = buffer;
            sendData();
        }
    }

    @Override
    protected void write(CompoundTag tag, boolean clientPacket) {
        super.write(tag, clientPacket);
        tag.m_128356_("Buffer", buffer);
        tag.m_128347_("Resto", resto);
    }

    @Override
    protected void read(CompoundTag tag, boolean clientPacket) {
        super.read(tag, clientPacket);
        // Tudo opcional: NBT vazio ({}) ou de versão antiga carrega como dínamo vazio.
        long b = tag.m_128425_("Buffer", 99) ? tag.m_128454_("Buffer") : 0;
        buffer = Math.max(0, Math.min(getBufferMax(), b));
        double r = tag.m_128425_("Resto", 99) ? tag.m_128459_("Resto") : 0;
        resto = Double.isFinite(r) && r > 0 && r < 1 ? r : 0;
    }

    @Override
    public boolean addToGoggleTooltip(List<Component> tooltip, boolean isPlayerSneaking) {
        super.addToGoggleTooltip(tooltip, isPlayerSneaking);
        DinamoBlock.Tier t = getTier();
        double eut = getEuT();
        tooltip.add(Component.m_237113_("    Dínamo Cinético (" + t.name() + ")").m_130940_(ChatFormatting.GOLD));
        tooltip.add(Component.m_237113_("    Tier: " + t.name() + " (" + t.voltagem + " V, 1 A)")
                .m_130940_(ChatFormatting.GRAY));
        tooltip.add(Component.m_237113_("    Geração: " + String.format(Locale.ROOT, "%.1f", eut).replace('.', ',')
                + " EU/t (máx. " + t.voltagem + ")").m_130940_(ChatFormatting.GRAY));
        tooltip.add(Component.m_237113_("    Energia: " + buffer + " / " + getBufferMax() + " EU")
                .m_130940_(ChatFormatting.GRAY));
        if (eut <= 0)
            tooltip.add(Component.m_237113_("    Sem rotação: dínamo parado").m_130940_(ChatFormatting.RED));
        return true;
    }

    /** Lado de saída visto pelo GregTech: só entrega (nada entra), na voltagem da tier, 1 A. */
    private final class Saida implements IEnergyContainer {
        @Override
        public long acceptEnergyFromNetwork(Direction lado, long voltagem, long amperes) {
            return 0;
        }

        @Override
        public boolean inputsEnergy(Direction lado) {
            return false;
        }

        @Override
        public boolean outputsEnergy(Direction lado) {
            return lado == faceSaida();
        }

        @Override
        public long changeEnergy(long delta) {
            if (delta >= 0) return 0;  // não aceita energia de fora
            long tirar = Math.min(buffer, -delta);
            buffer -= tirar;
            if (tirar > 0) m_6596_();
            return -tirar;
        }

        @Override
        public long getEnergyStored() {
            return buffer;
        }

        @Override
        public long getEnergyCapacity() {
            return getBufferMax();
        }

        @Override
        public long getInputAmperage() {
            return 0;
        }

        @Override
        public long getInputVoltage() {
            return 0;
        }

        @Override
        public long getOutputVoltage() {
            return getVoltagem();
        }

        @Override
        public long getOutputAmperage() {
            return 1;
        }
    }

    /**
     * Capability de energia, anexada pelo AttachCapabilitiesEvent (EcosMaquinas), como a do motor: só na face de saída
     * (e lado null). O evento roda no construtor de BlockEntity, antes dos campos daqui existirem: tudo é lido na hora.
     */
    static final class Caps implements ICapabilityProvider {
        private final DinamoBlockEntity be;
        private LazyOptional<IEnergyContainer> energia = LazyOptional.empty();

        Caps(DinamoBlockEntity be) {
            this.be = be;
        }

        @Override
        public <T> LazyOptional<T> getCapability(Capability<T> cap, Direction lado) {
            if (cap != GTCapability.CAPABILITY_ENERGY_CONTAINER || be.saida == null) return LazyOptional.empty();
            if (lado != null && lado != be.faceSaida()) return LazyOptional.empty();
            if (!energia.isPresent()) energia = LazyOptional.of(() -> be.saida);
            return energia.cast();
        }

        void invalidar() {
            energia.invalidate();
        }
    }
}
