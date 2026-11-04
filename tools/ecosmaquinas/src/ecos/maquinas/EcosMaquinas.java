package ecos.maquinas;

import com.simibubi.create.api.stress.BlockStressValues;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraftforge.event.BuildCreativeModeTabContentsEvent;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.event.lifecycle.FMLCommonSetupEvent;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.function.Supplier;

/**
 * Ecos do Selo: blocos que ligam o Create ao GregTech (Motor a Vapor do Eco, Dínamo Cinético ULV/LV, Saída de Vapor).
 * Compilado contra os jars em SRG (nomes m_/f_ do Minecraft), como o ecosbridge.
 */
@Mod(EcosMaquinas.MODID)
public final class EcosMaquinas {
    public static final String MODID = "ecosmaquinas";
    private static final Logger LOG = LoggerFactory.getLogger(MODID);

    /** Balanço do ciclo vapor -> rotação -> EU. GregTech: 2 mB de vapor = 1 EU; aqui 2 mB -> 48 SU -> 0,75 EU (perda 25 %). */
    public static final class Constantes {
        public static final int SU_POR_MB_VAPOR = 24;
        public static final int SU_POR_EU = 64;
        public static final int MOTOR_RPM = 32;
        public static final int MOTOR_MAX_MB_T = 80;
        public static final int SAIDA_MB_T_POR_NIVEL = 6;
        public static final int DINAMO_ULV_IMPACTO = 8;
        public static final int DINAMO_LV_IMPACTO = 32;
    }

    public static final DeferredRegister<Block> BLOCKS = DeferredRegister.create(ForgeRegistries.BLOCKS, MODID);
    public static final DeferredRegister<Item> ITEMS = DeferredRegister.create(ForgeRegistries.ITEMS, MODID);
    public static final DeferredRegister<BlockEntityType<?>> BLOCK_ENTITIES =
            DeferredRegister.create(ForgeRegistries.BLOCK_ENTITY_TYPES, MODID);

    public static final RegistryObject<MotorVaporBlock> MOTOR_VAPOR =
            bloco("motor_vapor", () -> new MotorVaporBlock(props()));
    public static final RegistryObject<DinamoBlock> DINAMO_ULV =
            bloco("dinamo_cinetico_ulv", () -> new DinamoBlock(props(), DinamoBlock.Tier.ULV));
    public static final RegistryObject<DinamoBlock> DINAMO_LV =
            bloco("dinamo_cinetico_lv", () -> new DinamoBlock(props(), DinamoBlock.Tier.LV));
    public static final RegistryObject<SaidaVaporBlock> SAIDA_VAPOR =
            bloco("saida_vapor", () -> new SaidaVaporBlock(props()));

    public static final RegistryObject<BlockEntityType<MotorVaporBlockEntity>> MOTOR_VAPOR_BE =
            BLOCK_ENTITIES.register("motor_vapor", () -> BlockEntityType.Builder.m_155273_(
                    (pos, state) -> new MotorVaporBlockEntity(EcosMaquinas.MOTOR_VAPOR_BE.get(), pos, state),
                    MOTOR_VAPOR.get()).m_58966_(null));
    public static final RegistryObject<BlockEntityType<DinamoBlockEntity>> DINAMO_BE =
            BLOCK_ENTITIES.register("dinamo_cinetico", () -> BlockEntityType.Builder.m_155273_(
                    (pos, state) -> new DinamoBlockEntity(EcosMaquinas.DINAMO_BE.get(), pos, state),
                    DINAMO_ULV.get(), DINAMO_LV.get()).m_58966_(null));
    public static final RegistryObject<BlockEntityType<SaidaVaporBlockEntity>> SAIDA_VAPOR_BE =
            BLOCK_ENTITIES.register("saida_vapor", () -> BlockEntityType.Builder.m_155273_(
                    (pos, state) -> new SaidaVaporBlockEntity(EcosMaquinas.SAIDA_VAPOR_BE.get(), pos, state),
                    SAIDA_VAPOR.get()).m_58966_(null));

    public EcosMaquinas() {
        IEventBus bus = FMLJavaModLoadingContext.get().getModEventBus();
        BLOCKS.register(bus);
        ITEMS.register(bus);
        BLOCK_ENTITIES.register(bus);
        bus.addListener(this::setup);
        bus.addListener(this::abaCriativa);
    }

    /** Metal: dureza 3,5 / resistência 6, som de metal (SoundType.METAL = f_56743_ em SRG). */
    private static BlockBehaviour.Properties props() {
        return BlockBehaviour.Properties.m_284310_().m_60913_(3.5f, 6.0f).m_60918_(SoundType.f_56743_);
    }

    private static <B extends Block> RegistryObject<B> bloco(String nome, Supplier<B> fabrica) {
        RegistryObject<B> b = BLOCKS.register(nome, fabrica);
        ITEMS.register(nome, () -> new BlockItem(b.get(), new Item.Properties()));
        return b;
    }

    private void setup(FMLCommonSetupEvent event) {
        event.enqueueWork(() -> {
            // Create 6: valores por RPM. O motor gira a MOTOR_RPM e no máximo dá SU_POR_MB_VAPOR * MOTOR_MAX_MB_T SU.
            BlockStressValues.CAPACITIES.register(MOTOR_VAPOR.get(), () ->
                    (double) Constantes.SU_POR_MB_VAPOR * Constantes.MOTOR_MAX_MB_T / Constantes.MOTOR_RPM);
            BlockStressValues.RPM.register(MOTOR_VAPOR.get(),
                    new BlockStressValues.GeneratedRpm(Constantes.MOTOR_RPM, true));
            BlockStressValues.IMPACTS.register(DINAMO_ULV.get(), () -> (double) Constantes.DINAMO_ULV_IMPACTO);
            BlockStressValues.IMPACTS.register(DINAMO_LV.get(), () -> (double) Constantes.DINAMO_LV_IMPACTO);
            LOG.info("[ecos] ecosmaquinas: valores de stress registrados no Create");
        });
    }

    /** Põe os blocos na aba principal do Create (id create:base). */
    private void abaCriativa(BuildCreativeModeTabContentsEvent event) {
        if (!"create:base".equals(event.getTabKey().m_135782_().toString())) return;
        event.accept(MOTOR_VAPOR);
        event.accept(DINAMO_ULV);
        event.accept(DINAMO_LV);
        event.accept(SAIDA_VAPOR);
    }
}
