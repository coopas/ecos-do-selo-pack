package ecos.maquinas.cliente;

import com.simibubi.create.AllPartialModels;
import com.simibubi.create.content.kinetics.base.KineticBlockEntityRenderer;
import ecos.maquinas.MotorVaporBlockEntity;
import net.createmod.catnip.render.CachedBuffers;
import net.createmod.catnip.render.SuperByteBuffer;
import net.minecraft.client.renderer.blockentity.BlockEntityRendererProvider;
import net.minecraft.world.level.block.state.BlockState;

/** SÓ CLIENTE. Meio eixo girando na face do eixo (igual ao CreativeMotorRenderer), usado quando o Flywheel está desligado. */
public class MotorVaporRenderer extends KineticBlockEntityRenderer<MotorVaporBlockEntity> {
    public MotorVaporRenderer(BlockEntityRendererProvider.Context context) {
        super(context);
    }

    @Override
    protected SuperByteBuffer getRotatedModel(MotorVaporBlockEntity be, BlockState state) {
        return CachedBuffers.partialFacing(AllPartialModels.SHAFT_HALF, state);
    }
}
