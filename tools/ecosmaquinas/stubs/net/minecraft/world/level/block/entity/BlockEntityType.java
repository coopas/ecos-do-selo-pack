package net.minecraft.world.level.block.entity;

import com.mojang.datafixers.types.Type;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;

/**
 * STUB SÓ DE COMPILAÇÃO (não vai no jar). No vanilla, BlockEntitySupplier é privado; o Forge o torna público em tempo de
 * execução pelo accesstransformer.cfg ("public net.minecraft.world.level.block.entity.BlockEntityType$BlockEntitySupplier").
 * Como compilamos contra o jar SRG sem ATs aplicados, este stub reproduz só as assinaturas usadas, com os mesmos
 * descritores do jar real (m_155273_ = Builder.of, m_58966_ = Builder.build, m_155267_ = BlockEntitySupplier.create).
 */
public class BlockEntityType<T extends BlockEntity> {
    public interface BlockEntitySupplier<T extends BlockEntity> {
        T m_155267_(BlockPos pos, BlockState state);
    }

    public static final class Builder<T extends BlockEntity> {
        public static <T extends BlockEntity> Builder<T> m_155273_(BlockEntitySupplier<? extends T> supplier, Block... blocks) {
            throw new UnsupportedOperationException("stub");
        }

        public BlockEntityType<T> m_58966_(Type<?> type) {
            throw new UnsupportedOperationException("stub");
        }
    }
}
