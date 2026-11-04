package ecos.maquinas.cliente;

import com.simibubi.create.AllPartialModels;
import com.simibubi.create.content.kinetics.base.KineticBlockEntityRenderer;
import ecos.maquinas.DinamoBlockEntity;
import net.createmod.catnip.render.CachedBuffers;
import net.createmod.catnip.render.SuperByteBuffer;
import net.minecraft.client.renderer.blockentity.BlockEntityRendererProvider;
import net.minecraft.world.level.block.state.BlockState;

/** SÓ CLIENTE. Meio eixo girando na face do eixo dos dínamos (ULV e LV), usado quando o Flywheel está desligado. */
public class DinamoRenderer extends KineticBlockEntityRenderer<DinamoBlockEntity> {
    public DinamoRenderer(BlockEntityRendererProvider.Context context) {
        super(context);
    }

    @Override
    protected SuperByteBuffer getRotatedModel(DinamoBlockEntity be, BlockState state) {
        return CachedBuffers.partialFacing(AllPartialModels.SHAFT_HALF, state);
    }
}
