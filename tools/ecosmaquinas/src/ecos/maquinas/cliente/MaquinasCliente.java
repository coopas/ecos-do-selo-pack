package ecos.maquinas.cliente;

import com.simibubi.create.AllPartialModels;
import com.simibubi.create.content.kinetics.base.OrientedRotatingVisual;
import dev.engine_room.flywheel.lib.visualization.SimpleBlockEntityVisualizer;
import ecos.maquinas.EcosMaquinas;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.fml.event.lifecycle.FMLClientSetupEvent;

/**
 * SÓ CLIENTE. Meio eixo do Create saindo da face FACING do motor e dos dínamos, girando com a rede (como o motor criativo):
 * visual do Flywheel quando ele está ativo e, sem Flywheel, o renderizador de block entity.
 * Chamado de EcosMaquinas só quando FMLEnvironment.dist é CLIENT.
 */
public final class MaquinasCliente {
    private MaquinasCliente() {
    }

    public static void registrar(IEventBus bus) {
        bus.addListener(MaquinasCliente::renderizadores);
        bus.addListener(MaquinasCliente::setup);
    }

    private static void renderizadores(EntityRenderersEvent.RegisterRenderers event) {
        event.registerBlockEntityRenderer(EcosMaquinas.MOTOR_VAPOR_BE.get(), MotorVaporRenderer::new);
        event.registerBlockEntityRenderer(EcosMaquinas.DINAMO_BE.get(), DinamoRenderer::new);
    }

    private static void setup(FMLClientSetupEvent event) {
        event.enqueueWork(() -> {
            SimpleBlockEntityVisualizer.builder(EcosMaquinas.MOTOR_VAPOR_BE.get())
                    .factory(OrientedRotatingVisual.of(AllPartialModels.SHAFT_HALF))
                    .skipVanillaRender(be -> true)
                    .apply();
            SimpleBlockEntityVisualizer.builder(EcosMaquinas.DINAMO_BE.get())
                    .factory(OrientedRotatingVisual.of(AllPartialModels.SHAFT_HALF))
                    .skipVanillaRender(be -> true)
                    .apply();
        });
    }
}
