package ecos.maquinas;

import com.simibubi.create.content.kinetics.base.DirectionalKineticBlock;
import com.simibubi.create.content.kinetics.base.GeneratingKineticBlockEntity;
import ecos.maquinas.EcosMaquinas.Constantes;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.common.capabilities.Capability;
import net.minecraftforge.common.capabilities.ForgeCapabilities;
import net.minecraftforge.common.capabilities.ICapabilityProvider;
import net.minecraftforge.common.util.LazyOptional;
import net.minecraftforge.fluids.FluidStack;
import net.minecraftforge.fluids.capability.IFluidHandler;
import net.minecraftforge.fluids.capability.templates.FluidTank;
import net.minecraftforge.registries.ForgeRegistries;

import java.util.List;
import java.util.Locale;

/**
 * Motor a Vapor do Eco: vapor do GregTech (gtceu:steam) entra num tanque de 8 000 mB por qualquer face menos a do eixo;
 * por tick o motor queima até MOTOR_MAX_MB_T e gira a MOTOR_RPM com capacidade SU_POR_MB_VAPOR * consumo / MOTOR_RPM
 * por RPM (80 mB/t -> 60 SU/RPM -> 1920 SU). Sem vapor (ou com outro fluido) fica em 0 RPM.
 *
 * O consumo vale pela média de uma janela de JANELA ticks: a rede do Create só é recalculada quando a média muda,
 * não a cada tick. O vapor queimado numa janela paga a rotação da janela seguinte.
 *
 * NBT: "Tanque" (FluidTank) e "Consumo" (mB/t). Os dois são opcionais: motores salvos sem eles (Task 3) carregam vazios.
 */
public class MotorVaporBlockEntity extends GeneratingKineticBlockEntity {
    public static final int TANQUE_MB = 8000;
    static final ResourceLocation VAPOR = new ResourceLocation("gtceu", "steam");
    private static final int JANELA = 10;

    private final FluidTank tanque = new FluidTank(TANQUE_MB, MotorVaporBlockEntity::ehVapor) {
        @Override
        protected void onContentsChanged() {
            m_6596_();  // setChanged
        }
    };
    /** O que os canos veem: só enche (e só com vapor); não deixa puxar o vapor de volta. */
    private final IFluidHandler entrada = new Entrada();
    private float consumoMbT;
    private int gastoJanela, ticksJanela, ultimoSync = -1;

    public MotorVaporBlockEntity(BlockEntityType<?> type, BlockPos pos, BlockState state) {
        super(type, pos, state);
    }

    static boolean ehVapor(FluidStack fs) {
        return fs != null && !fs.isEmpty() && VAPOR.equals(ForgeRegistries.FLUIDS.getKey(fs.getFluid()));
    }

    /** Face do eixo (FACING); null se o estado não for de motor. */
    Direction eixo() {
        BlockState s = m_58900_();
        return s.m_61138_(DirectionalKineticBlock.FACING) ? s.m_61143_(DirectionalKineticBlock.FACING) : null;
    }

    /** mB de vapor no tanque (usado pelo script dev e pelo tooltip). */
    public int getVapor() {
        return tanque.getFluidAmount();
    }

    /** Consumo médio da última janela, em mB/t: é ele que define a rotação e a capacidade. */
    public float getConsumoMbT() {
        return consumoMbT;
    }

    @Override
    public void tick() {
        super.tick();
        if (f_58857_ == null || f_58857_.f_46443_) return;
        gastoJanela += tanque.drain(Constantes.MOTOR_MAX_MB_T, IFluidHandler.FluidAction.EXECUTE).getAmount();
        if (++ticksJanela < JANELA) return;
        float media = (float) gastoJanela / JANELA;
        gastoJanela = 0;
        ticksJanela = 0;
        if (media != consumoMbT) {
            consumoMbT = media;
            m_6596_();
            updateGeneratedRotation();  // velocidade, capacidade na rede e sendData
        }
    }

    @Override
    public void lazyTick() {
        super.lazyTick();
        if (f_58857_ == null || f_58857_.f_46443_) return;
        if (tanque.getFluidAmount() != ultimoSync) {  // tooltip do cliente acompanha o tanque sem mandar pacote todo tick
            ultimoSync = tanque.getFluidAmount();
            sendData();
        }
    }

    @Override
    public float getGeneratedSpeed() {
        Direction d = eixo();
        if (consumoMbT <= 0 || d == null) return 0;
        return convertToDirection(Constantes.MOTOR_RPM, d);
    }

    @Override
    public float calculateAddedStressCapacity() {
        float c = Constantes.SU_POR_MB_VAPOR * consumoMbT / Constantes.MOTOR_RPM;
        lastCapacityProvided = c;
        return c;
    }

    @Override
    protected void write(CompoundTag tag, boolean clientPacket) {
        super.write(tag, clientPacket);
        tag.m_128365_("Tanque", tanque.writeToNBT(new CompoundTag()));
        tag.m_128350_("Consumo", consumoMbT);
    }

    @Override
    protected void read(CompoundTag tag, boolean clientPacket) {
        super.read(tag, clientPacket);
        // Tudo opcional: NBT vazio ({}) ou de versão antiga carrega como motor vazio e parado.
        tanque.setFluid(FluidStack.EMPTY);
        if (tag.m_128425_("Tanque", 10)) tanque.readFromNBT(tag.m_128469_("Tanque"));
        FluidStack f = tanque.getFluid();
        if (!ehVapor(f)) tanque.setFluid(FluidStack.EMPTY);  // fluido estranho no NBT: descarta
        else if (f.getAmount() > TANQUE_MB) f.setAmount(TANQUE_MB);
        float c = tag.m_128425_("Consumo", 99) ? tag.m_128457_("Consumo") : 0;
        consumoMbT = Float.isFinite(c) ? Math.max(0, Math.min(Constantes.MOTOR_MAX_MB_T, c)) : 0;
    }

    @Override
    public boolean addToGoggleTooltip(List<Component> tooltip, boolean isPlayerSneaking) {
        super.addToGoggleTooltip(tooltip, isPlayerSneaking);
        tooltip.add(Component.m_237113_("    Motor a Vapor do Eco").m_130940_(ChatFormatting.GOLD));
        tooltip.add(Component.m_237113_("    Vapor: " + tanque.getFluidAmount() + " / " + TANQUE_MB + " mB")
                .m_130940_(ChatFormatting.GRAY));
        tooltip.add(Component.m_237113_("    Consumo: " + String.format(Locale.ROOT, "%.1f", consumoMbT).replace('.', ',')
                + " mB/t (máx. " + Constantes.MOTOR_MAX_MB_T + ")").m_130940_(ChatFormatting.GRAY));
        if (consumoMbT <= 0)
            tooltip.add(Component.m_237113_("    Sem vapor: motor parado").m_130940_(ChatFormatting.RED));
        return true;
    }

    private final class Entrada implements IFluidHandler {
        @Override
        public int getTanks() {
            return 1;
        }

        @Override
        public FluidStack getFluidInTank(int t) {
            return tanque.getFluidInTank(t);
        }

        @Override
        public int getTankCapacity(int t) {
            return tanque.getTankCapacity(t);
        }

        @Override
        public boolean isFluidValid(int t, FluidStack fs) {
            return ehVapor(fs);
        }

        @Override
        public int fill(FluidStack fs, FluidAction acao) {
            return ehVapor(fs) ? tanque.fill(fs, acao) : 0;
        }

        @Override
        public FluidStack drain(FluidStack fs, FluidAction acao) {
            return FluidStack.EMPTY;
        }

        @Override
        public FluidStack drain(int mb, FluidAction acao) {
            return FluidStack.EMPTY;
        }
    }

    /**
     * Capability de fluido, anexada pelo AttachCapabilitiesEvent (EcosMaquinas): o jar de compilação é o MC sem os
     * patches do Forge, então não dá para sobrescrever getCapability chamando super. Todas as faces menos a do eixo.
     * O evento roda no construtor de BlockEntity, antes dos campos daqui existirem: tudo é lido na hora do pedido.
     */
    static final class Caps implements ICapabilityProvider {
        private final MotorVaporBlockEntity be;
        private LazyOptional<IFluidHandler> fluido = LazyOptional.empty();

        Caps(MotorVaporBlockEntity be) {
            this.be = be;
        }

        @Override
        public <T> LazyOptional<T> getCapability(Capability<T> cap, Direction lado) {
            if (cap != ForgeCapabilities.FLUID_HANDLER || be.entrada == null) return LazyOptional.empty();
            if (lado != null && lado == be.eixo()) return LazyOptional.empty();
            if (!fluido.isPresent()) fluido = LazyOptional.of(() -> be.entrada);
            return fluido.cast();
        }

        void invalidar() {
            fluido.invalidate();
        }
    }
}
