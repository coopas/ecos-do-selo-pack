package ecos.maquinas;

import com.simibubi.create.content.kinetics.base.GeneratingKineticBlockEntity;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;

/** Gera rotação a partir de vapor do GregTech. Corpo na Task 4; por enquanto não gira (0 RPM) e não guarda NBT próprio. */
public class MotorVaporBlockEntity extends GeneratingKineticBlockEntity {
    public MotorVaporBlockEntity(BlockEntityType<?> type, BlockPos pos, BlockState state) {
        super(type, pos, state);
    }

    @Override
    public float getGeneratedSpeed() {
        return 0;
    }
}
