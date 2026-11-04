package ecos.maquinas;

import com.simibubi.create.foundation.block.IBE;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.entity.BlockEntityType;

/**
 * Saída de Vapor: encosta numa caldeira do Create (tanque de fluido) e entrega gtceu:steam aos vizinhos.
 * IBE dá o BlockEntity e o ticker do Create (SmartBlockEntityTicker) para a lógica em SaidaVaporBlockEntity.
 */
public class SaidaVaporBlock extends Block implements IBE<SaidaVaporBlockEntity> {
    public SaidaVaporBlock(Properties props) {
        super(props);
    }

    @Override
    public Class<SaidaVaporBlockEntity> getBlockEntityClass() {
        return SaidaVaporBlockEntity.class;
    }

    @Override
    public BlockEntityType<? extends SaidaVaporBlockEntity> getBlockEntityType() {
        return EcosMaquinas.SAIDA_VAPOR_BE.get();
    }
}
