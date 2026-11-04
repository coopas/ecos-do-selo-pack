package ecos.maquinas;

import com.simibubi.create.content.kinetics.base.DirectionalKineticBlock;
import com.simibubi.create.foundation.block.IBE;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.level.LevelReader;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;

/** Dínamo Cinético: eixo do Create na face FACING; a tier (ULV/LV) vem do bloco. */
public class DinamoBlock extends DirectionalKineticBlock implements IBE<DinamoBlockEntity> {
    public enum Tier {
        ULV(8, EcosMaquinas.Constantes.DINAMO_ULV_IMPACTO),
        LV(32, EcosMaquinas.Constantes.DINAMO_LV_IMPACTO);

        /** Voltagem do GregTech (EU/t por ampere). */
        public final long voltagem;
        /** Impacto no Create, em SU por RPM. */
        public final int impacto;

        Tier(long voltagem, int impacto) {
            this.voltagem = voltagem;
            this.impacto = impacto;
        }
    }

    public final Tier tier;

    public DinamoBlock(Properties props, Tier tier) {
        super(props);
        this.tier = tier;
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
    public Class<DinamoBlockEntity> getBlockEntityClass() {
        return DinamoBlockEntity.class;
    }

    @Override
    public BlockEntityType<? extends DinamoBlockEntity> getBlockEntityType() {
        return EcosMaquinas.DINAMO_BE.get();
    }
}
