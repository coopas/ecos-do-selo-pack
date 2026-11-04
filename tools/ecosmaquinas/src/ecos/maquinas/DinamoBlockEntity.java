package ecos.maquinas;

import com.simibubi.create.content.kinetics.base.KineticBlockEntity;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;

/** Consome rotação do Create (impacto registrado em BlockStressValues.IMPACTS). Geração de EU na Task 5. */
public class DinamoBlockEntity extends KineticBlockEntity {
    public DinamoBlockEntity(BlockEntityType<?> type, BlockPos pos, BlockState state) {
        super(type, pos, state);
    }
}
