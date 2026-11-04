package ecos.bridge;

import dev.ftb.mods.ftbfiltersystem.api.FTBFilterSystemAPI;
import dev.ftb.mods.ftbquests.api.FTBQuestsAPI;
import dev.ftb.mods.ftbquests.api.ItemFilterAdapter;
import net.minecraft.tags.TagKey;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.event.lifecycle.FMLCommonSetupEvent;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Ecos do Selo: liga os smart filters do FTB Filter System às tasks do FTB Quests.
 * O FTB Quests 2001.4 só casa itens com filtros via ItemFilterAdapter registrado, e o FTB Filter System 20.0.1
 * não registra nenhum. Feito em Java (não KubeJS) porque o livro de quests chama isso no thread de render.
 */
@Mod("ecosbridge")
public final class EcosBridge {
    private static final Logger LOG = LoggerFactory.getLogger("ecosbridge");

    public EcosBridge() {
        FMLJavaModLoadingContext.get().getModEventBus().addListener(this::setup);
    }

    private void setup(FMLCommonSetupEvent event) {
        event.enqueueWork(() -> {
            FTBQuestsAPI.api().registerFilterAdapter(new Adapter());
            LOG.info("[ecos] adaptador FTB Filter System -> FTB Quests registrado (Java)");
        });
    }

    static final class Adapter implements ItemFilterAdapter {
        @Override public String getName() { return "ecos_ftbfiltersystem"; }

        @Override public boolean isFilterStack(ItemStack stack) {
            try { return FTBFilterSystemAPI.api().isFilterItem(stack); } catch (RuntimeException e) { return false; }
        }

        @Override public boolean doesItemMatch(ItemStack filter, ItemStack stack) {
            try { return FTBFilterSystemAPI.api().doesFilterMatch(filter, stack); } catch (RuntimeException e) { return false; }
        }

        @Override public Matcher getMatcher(ItemStack filter) {
            return stack -> doesItemMatch(filter, stack);
        }

        @Override public boolean hasItemTagFilter() { return true; }

        @Override public ItemStack makeTagFilterStack(TagKey<Item> tag) {
            return FTBFilterSystemAPI.api().makeTagFilter(tag);
        }
    }
}
