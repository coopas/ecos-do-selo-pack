package ecos.bridge;

import com.mojang.blaze3d.platform.InputConstants;
import net.minecraft.client.KeyMapping;
import net.minecraft.client.Minecraft;
import net.minecraftforge.fml.event.lifecycle.FMLClientSetupEvent;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.nio.file.Files;
import java.nio.file.Path;

/**
 * Só no cliente: o Full Brightness Toggle vem no G, que no pack já é Curios, ProjectE, GuideME, Ars e jetpack do GT.
 * Na primeira vez (o options.txt ainda não tem a tecla dele) passa para o J, que está livre. Depois disso
 * o options.txt guarda a escolha e o jogador troca à vontade em Opções → Controles.
 */
// Nomes SRG (o build compila contra o client-srg): getInstance, gameDirectory, options.keyMappings, getName,
// setKey, resetMapping, options.save e InputConstants.getKey.
final class ClientKeys {
    private static final Logger LOG = LoggerFactory.getLogger("ecosbridge");
    static final String FULLBRIGHT = "fullbrightnesstoggle.key.togglebrightness";
    static final String FULLBRIGHT_KEY = "key.keyboard.j";

    private ClientKeys() {}

    static void setup(FMLClientSetupEvent event) {
        event.enqueueWork(ClientKeys::rebindFullbright);
    }

    private static void rebindFullbright() {
        try {
            Minecraft mc = Minecraft.m_91087_();
            Path options = mc.f_91069_.toPath().resolve("options.txt");
            if (Files.exists(options) && Files.readString(options).contains("key_" + FULLBRIGHT + ":")) {
                return;
            }
            for (KeyMapping k : mc.f_91066_.f_92059_) {
                if (FULLBRIGHT.equals(k.m_90860_())) {
                    k.m_90848_(InputConstants.m_84851_(FULLBRIGHT_KEY));  // setKey
                    KeyMapping.m_90854_();
                    mc.f_91066_.m_92169_();
                    LOG.info("[ecos] tecla do fullbright -> J");
                    return;
                }
            }
            LOG.warn("[ecos] tecla do fullbright não encontrada (mod ausente?)");
        } catch (Exception e) {
            LOG.warn("[ecos] não consegui trocar a tecla do fullbright", e);
        }
    }
}
