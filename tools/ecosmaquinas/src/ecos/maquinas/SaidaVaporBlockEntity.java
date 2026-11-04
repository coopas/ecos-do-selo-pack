package ecos.maquinas;

import net.minecraft.core.BlockPos;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;

/** Entrega vapor do GregTech a partir da caldeira do Create. Corpo na Task 6; por enquanto não faz nada nem guarda NBT. */
public class SaidaVaporBlockEntity extends BlockEntity {
    public SaidaVaporBlockEntity(BlockEntityType<?> type, BlockPos pos, BlockState state) {
        super(type, pos, state);
    }
}
