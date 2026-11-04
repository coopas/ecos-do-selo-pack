package ecos.maquinas;

import com.simibubi.create.content.kinetics.base.DirectionalKineticBlock;
import com.simibubi.create.foundation.block.IBE;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.level.LevelReader;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;

/** Motor a Vapor do Eco: eixo do Create na face FACING. */
public class MotorVaporBlock extends DirectionalKineticBlock implements IBE<MotorVaporBlockEntity> {
    public MotorVaporBlock(Properties props) {
        super(props);
    }

    @Override
    public boolean hasShaftTowards(LevelReader world, BlockPos pos, BlockState state, Direction face) {
        return face == state.m_61143_(FACING);
    }

    @Override
    public Direction.Axis getRotationAxis(BlockState state) {
        return state.m_61143_(FACING).m_122434_();
    }

    @Override
    public Class<MotorVaporBlockEntity> getBlockEntityClass() {
        return MotorVaporBlockEntity.class;
    }

    @Override
    public BlockEntityType<? extends MotorVaporBlockEntity> getBlockEntityType() {
        return EcosMaquinas.MOTOR_VAPOR_BE.get();
    }
}
