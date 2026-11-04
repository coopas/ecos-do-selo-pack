package ecos.maquinas;

import net.minecraft.core.BlockPos;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.EntityBlock;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;

/** Saída de Vapor: encosta numa caldeira do Create (lógica na Task 6). */
public class SaidaVaporBlock extends Block implements EntityBlock {
    public SaidaVaporBlock(Properties props) {
        super(props);
    }

    @Override
    public BlockEntity m_142194_(BlockPos pos, BlockState state) {
        return new SaidaVaporBlockEntity(EcosMaquinas.SAIDA_VAPOR_BE.get(), pos, state);
    }
}
