package ecos.maquinas;

import com.simibubi.create.api.equipment.goggles.IHaveGoggleInformation;
import com.simibubi.create.content.fluids.tank.BoilerData;
import com.simibubi.create.content.fluids.tank.FluidTankBlockEntity;
import com.simibubi.create.foundation.blockEntity.SmartBlockEntity;
import com.simibubi.create.foundation.blockEntity.behaviour.BlockEntityBehaviour;
import com.simibubi.create.foundation.fluid.FluidHelper;
import ecos.maquinas.EcosMaquinas.Constantes;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.material.Fluid;
import net.minecraftforge.common.capabilities.ForgeCapabilities;
import net.minecraftforge.common.capabilities.ICapabilityProvider;
import net.minecraftforge.fluids.FluidStack;
import net.minecraftforge.fluids.capability.IFluidHandler;
import net.minecraftforge.fluids.capability.templates.FluidTank;
import net.minecraftforge.registries.ForgeRegistries;

import java.util.List;
import java.util.Map;
import java.util.WeakHashMap;

/**
 * Saída de Vapor: encostada numa caldeira do Create (FluidTankBlockEntity), entrega SAIDA_MB_T_POR_NIVEL mB/t de
 * gtceu:steam por nível aos vizinhos com FLUID_HANDLER (menos tanques do Create).
 *
 * Nível = min(activeHeat, getMaxHeatLevelForBoilerSize(tamanho), limite de água): o mesmo limite que o Create aplica
 * aos motores. Modo exclusivo: com qualquer motor a vapor do Create acoplado (attachedEngines > 0) ou qualquer apito
 * (attachedWhistles > 0) a saída dá 0. O apito também liga a caldeira no Create (que passa a sumir com a água
 * bombeada): ou o Create usa a caldeira, ou a saída.
 *
 * Água: sem motor nem apito a caldeira do Create fica inativa (BoilerData.isActive() == false): não atualiza o calor,
 * não mede a água e o tanque é um tanque comum. Então a saída refaz o calor com BoilerData.updateTemperature e gasta
 * a água do próprio tanque: AGUA_MB_POR_NIVEL (10 mB, o waterSupplyPerLevel do Create) por nível por tick, na
 * proporção do vapor de fato entregue (10 mB de água -> 6 mB de vapor). Sem água no tanque: 0.
 *
 * Várias saídas na mesma caldeira dividem um orçamento por tick (6 x nível mB): mais saídas não multiplicam o vapor.
 *
 * NBT: "Nivel", "Producao", "Estado" (só para o tooltip; o servidor recalcula a cada tick). Todos opcionais e
 * limitados: as saídas que já estão no mundo (Task 3) foram salvas com NBT vazio.
 */
public class SaidaVaporBlockEntity extends SmartBlockEntity implements IHaveGoggleInformation {
    /** BoilerData.waterSupplyPerLevel (privado no Create): 10 mB/t de água por nível de calor. */
    static final int AGUA_MB_POR_NIVEL = 10;
    static final int NIVEL_MAX = 18;
    private static final int TICKS_CALOR = 10;

    static final int SEM_CALDEIRA = 0, MOTOR_ACOPLADO = 1, SEM_CALOR = 2, SEM_AGUA = 3, SEM_DESTINO = 4,
            ESGOTADA = 5, PRODUZINDO = 6, APITO_ACOPLADO = 7;

    /** Vapor já entregue neste tick por caldeira (controlador): {tick do jogo, mB}. Só no servidor. */
    private static final Map<FluidTankBlockEntity, long[]> USO = new WeakHashMap<>();

    private int nivel, producao, estado = SEM_CALDEIRA;
    private int ticksCalor, syncNivel = -1, syncProducao = -1, syncEstado = -1;

    public SaidaVaporBlockEntity(BlockEntityType<?> type, BlockPos pos, BlockState state) {
        super(type, pos, state);
    }

    @Override
    public void addBehaviours(List<BlockEntityBehaviour> behaviours) {
    }

    /** Nível da caldeira que a saída está usando (0 sem caldeira, com motor ou apito, sem calor ou sem água). */
    public int getNivel() {
        return nivel;
    }

    /** Motivo do tooltip (SEM_CALDEIRA ... APITO_ACOPLADO); lido pelo teste em jogo. */
    public int getEstado() {
        return estado;
    }

    /** mB de vapor entregues no último tick. */
    public int getProducaoMbT() {
        return producao;
    }

    @Override
    public void tick() {
        super.tick();
        if (f_58857_ == null || f_58857_.f_46443_) return;
        produzir();
    }

    private void produzir() {
        nivel = 0;
        producao = 0;
        FluidTankBlockEntity c = caldeira();
        if (c == null) { estado = SEM_CALDEIRA; return; }
        BoilerData b = c.boiler;
        if (b.attachedEngines > 0) { estado = MOTOR_ACOPLADO; return; }  // ou rotação, ou vapor
        if (b.attachedWhistles > 0) { estado = APITO_ACOPLADO; return; }  // apito: a caldeira é do Create
        if (--ticksCalor <= 0) {
            ticksCalor = TICKS_CALOR;
            b.updateTemperature(c);  // caldeira inativa: o Create não atualiza o calor sozinho
        }
        int n = Math.min(b.activeHeat, b.getMaxHeatLevelForBoilerSize(c.getTotalTankSize()));
        if (n <= 0) { estado = SEM_CALOR; return; }
        FluidTank tanque = c.getTankInventory();
        FluidStack agua = tanque.getFluid();
        boolean temAgua = !agua.isEmpty() && FluidHelper.isWater(agua.getFluid());
        n = Math.min(n, temAgua ? agua.getAmount() / AGUA_MB_POR_NIVEL : 0);
        n = Math.min(n, NIVEL_MAX);
        if (n <= 0) { estado = SEM_AGUA; return; }
        nivel = n;

        long agora = f_58857_.m_46467_();  // getGameTime
        long[] uso = USO.computeIfAbsent(c, k -> new long[2]);
        if (uso[0] != agora) { uso[0] = agora; uso[1] = 0; }
        int livre = n * Constantes.SAIDA_MB_T_POR_NIVEL - (int) uso[1];
        if (livre <= 0) { estado = ESGOTADA; return; }

        int entregue = empurrar(livre);
        if (entregue <= 0) { estado = SEM_DESTINO; return; }
        uso[1] += entregue;
        producao = entregue;
        estado = PRODUZINDO;
        // 10 mB de água para cada 6 mB de vapor entregue, arredondando contra o jogador
        int gasto = (entregue * AGUA_MB_POR_NIVEL + Constantes.SAIDA_MB_T_POR_NIVEL - 1) / Constantes.SAIDA_MB_T_POR_NIVEL;
        tanque.drain(new FluidStack(agua.getFluid(), gasto), IFluidHandler.FluidAction.EXECUTE);
    }

    /** Controlador da caldeira encostada (o primeiro tanque do Create vizinho), ou null. */
    private FluidTankBlockEntity caldeira() {
        for (Direction d : Direction.values()) {
            BlockPos p = f_58858_.m_121945_(d);
            if (!f_58857_.m_46749_(p)) continue;  // não carrega chunk vizinho
            if (f_58857_.m_7702_(p) instanceof FluidTankBlockEntity t) {
                FluidTankBlockEntity c = t.getControllerBE();
                if (c != null) return c;
            }
        }
        return null;
    }

    /** Empurra até mb de vapor nos vizinhos com FLUID_HANDLER (menos tanques do Create e outras saídas). */
    private int empurrar(int mb) {
        Fluid vapor = ForgeRegistries.FLUIDS.getValue(MotorVaporBlockEntity.VAPOR);
        if (vapor == null) return 0;
        int resta = mb;
        for (Direction d : Direction.values()) {
            if (resta <= 0) break;
            BlockPos p = f_58858_.m_121945_(d);
            if (!f_58857_.m_46749_(p)) continue;
            BlockEntity viz = f_58857_.m_7702_(p);
            if (viz == null || viz instanceof FluidTankBlockEntity || viz instanceof SaidaVaporBlockEntity) continue;
            // O jar de compilação não tem os patches do Forge: em runtime todo BlockEntity é ICapabilityProvider.
            if (!((Object) viz instanceof ICapabilityProvider prov)) continue;
            IFluidHandler h = prov.getCapability(ForgeCapabilities.FLUID_HANDLER, d.m_122424_()).orElse(null);
            if (h == null) continue;
            resta -= Math.max(0, Math.min(resta, h.fill(new FluidStack(vapor, resta), IFluidHandler.FluidAction.EXECUTE)));
        }
        return mb - resta;
    }

    @Override
    public void lazyTick() {
        super.lazyTick();
        if (f_58857_ == null || f_58857_.f_46443_) return;
        if (nivel != syncNivel || producao != syncProducao || estado != syncEstado) {  // tooltip sem pacote todo tick
            syncNivel = nivel;
            syncProducao = producao;
            syncEstado = estado;
            m_6596_();  // setChanged
            sendData();
        }
    }

    @Override
    protected void write(CompoundTag tag, boolean clientPacket) {
        super.write(tag, clientPacket);
        tag.m_128405_("Nivel", nivel);
        tag.m_128405_("Producao", producao);
        tag.m_128405_("Estado", estado);
    }

    @Override
    protected void read(CompoundTag tag, boolean clientPacket) {
        super.read(tag, clientPacket);
        // Tudo opcional e limitado: NBT vazio ({}) ou adulterado carrega como saída parada.
        nivel = limitar(tag.m_128425_("Nivel", 99) ? tag.m_128451_("Nivel") : 0, 0, NIVEL_MAX);
        producao = limitar(tag.m_128425_("Producao", 99) ? tag.m_128451_("Producao") : 0, 0,
                NIVEL_MAX * Constantes.SAIDA_MB_T_POR_NIVEL);
        int e = tag.m_128425_("Estado", 99) ? tag.m_128451_("Estado") : SEM_CALDEIRA;
        estado = e >= SEM_CALDEIRA && e <= APITO_ACOPLADO ? e : SEM_CALDEIRA;
    }

    private static int limitar(int v, int min, int max) {
        return Math.max(min, Math.min(max, v));
    }

    @Override
    public boolean addToGoggleTooltip(List<Component> tooltip, boolean isPlayerSneaking) {
        tooltip.add(Component.m_237113_("    Saída de Vapor").m_130940_(ChatFormatting.GOLD));
        tooltip.add(Component.m_237113_("    Nível da caldeira: " + nivel).m_130940_(ChatFormatting.GRAY));
        tooltip.add(Component.m_237113_("    Vapor: " + producao + " mB/t (" + Constantes.SAIDA_MB_T_POR_NIVEL
                + " por nível, máx. " + NIVEL_MAX * Constantes.SAIDA_MB_T_POR_NIVEL + ")").m_130940_(ChatFormatting.GRAY));
        String aviso = switch (estado) {
            case SEM_CALDEIRA -> "Encoste num tanque do Create com queimador embaixo";
            case MOTOR_ACOPLADO -> "Motor a vapor do Create na caldeira: saída desligada";
            case APITO_ACOPLADO -> "Apito do Create na caldeira: saída desligada";
            case SEM_CALOR -> "Caldeira sem calor (ou pequena demais)";
            case SEM_AGUA -> "Caldeira sem água";
            case SEM_DESTINO -> "Nada recebendo o vapor";
            case ESGOTADA -> "Outra Saída já usa todo o vapor desta caldeira";
            default -> null;
        };
        if (aviso != null) tooltip.add(Component.m_237113_("    " + aviso).m_130940_(ChatFormatting.RED));
        return true;
    }
}
