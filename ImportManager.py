from LichessEvents import LichessEvents
import bge
import bpy
from DataManager import DataManager as DM
from ImportManagerEvents import ImportManagerEvents as IME
from collections import OrderedDict

class ImportManager(bge.types.KX_PythonComponent):
    args = OrderedDict([
    ])

    instance = None
    def start(self, args):
        ImportManager.instance = self
        self.scene = self.object.scene

        self.filepath = DM.getValue('default_blend')
            
        IME.instance.register_observer(self)
    
    def importBox(self):
        IME.sounds = []
        IME.customs = []
        IME.squares = {}

        with bpy.data.libraries.load(self.filepath) as (data_from, data_to):
            data_to.objects = [name for name in data_from.objects]
            data_to.collections = [name for name in data_from.collections]
            data_to.sounds = [name for name in data_from.sounds]
            data_to.scenes = [name for name in data_from.scenes]

        self.importEeveeSettings()

        assets_collection = bpy.data.collections["GameCollection"]
        
        for sound in data_to.sounds:
            IME.sounds.append(sound)

        for obj in data_to.objects:
            a = obj.users_collection
            assets_collection.objects.link(obj)
            converted_obj = self.object.scene.convertBlenderObject(obj)
            if len(a) > 0:
                if a[0].name.startswith("CUSTOM"):
                    IME.customs.append(converted_obj)
                elif a[0].name.startswith("SETTINGS"):
                    IME.settings.append(converted_obj)
                elif a[0].name.startswith("TOKEN"):
                    IME.tokens.append(converted_obj)
                elif a[0].name.startswith("STOCKFISH"):
                    IME.stockfishs.append(converted_obj)
                elif a[0].name.startswith("MOVES"):
                    IME.moves.append(converted_obj)

            if obj.name.startswith("Square_"):
                converted_obj["Clickable"] = True
                self.processSquare(converted_obj)

            elif obj.name.endswith("_btn"):
                converted_obj["Clickable"] = True

            elif obj.name.endswith("_checkbox"):
                converted_obj["Clickable"] = True

            elif obj.name.endswith("_slider"):
                converted_obj["Clickable"] = True

            elif obj.name.endswith("_custom"):
                converted_obj["Clickable"] = True
        
        IME.instance.newImport()
        self.object.scene.active_camera = self.object.scene.objects["Camera_Board"]

    def processSquare(self, square):
        square.worldPosition.x = round(square.worldPosition.x)
        square.worldPosition.z = round(square.worldPosition.z)
        string_index = square.name.replace("Square_", "")
        index = int(string_index)
        square['Square'] = index
        IME.squares[index] = square
    
    def update(self):
        pass

    def importEeveeSettings(self):
        game_scene = bpy.data.scenes["Chess_Scene"]
        imported_scene = bpy.data.scenes["BOX_Scene"]

        # Sampling
        game_scene.eevee.taa_render_samples   = imported_scene.eevee.taa_render_samples
        game_scene.eevee.taa_samples          = imported_scene.eevee.taa_samples
        game_scene.eevee.use_taa_reprojection = imported_scene.eevee.use_taa_reprojection

        # Ambient Occlusion
        game_scene.eevee.use_gtao               = imported_scene.eevee.use_gtao
        game_scene.eevee.gtao_distance          = imported_scene.eevee.gtao_distance
        game_scene.eevee.gtao_factor            = imported_scene.eevee.gtao_factor
        game_scene.eevee.gtao_quality           = imported_scene.eevee.gtao_quality
        game_scene.eevee.use_gtao_bent_normals  = imported_scene.eevee.use_gtao_bent_normals
        game_scene.eevee.use_gtao_bounce        = imported_scene.eevee.use_gtao_bounce

        # Bloom
        game_scene.eevee.use_bloom       = imported_scene.eevee.use_bloom
        game_scene.eevee.bloom_threshold = imported_scene.eevee.bloom_threshold
        game_scene.eevee.bloom_knee      = imported_scene.eevee.bloom_knee
        game_scene.eevee.bloom_radius    = imported_scene.eevee.bloom_radius
        game_scene.eevee.bloom_color     = imported_scene.eevee.bloom_color
        game_scene.eevee.bloom_intensity = imported_scene.eevee.bloom_intensity
        game_scene.eevee.bloom_clamp     = imported_scene.eevee.bloom_clamp

        # Depth of field
        game_scene.eevee.bokeh_max_size                        = imported_scene.eevee.bokeh_max_size
        game_scene.eevee.bokeh_threshold                       = imported_scene.eevee.bokeh_threshold
        game_scene.eevee.bokeh_neighbor_max                    = imported_scene.eevee.bokeh_neighbor_max
        game_scene.eevee.bokeh_denoise_fac                     = imported_scene.eevee.bokeh_denoise_fac
        game_scene.eevee.use_bokeh_high_quality_slight_defocus = imported_scene.eevee.use_bokeh_high_quality_slight_defocus
        game_scene.eevee.use_bokeh_jittered                    = imported_scene.eevee.use_bokeh_jittered
        game_scene.eevee.bokeh_overblur                        = imported_scene.eevee.bokeh_overblur

        # Subsurface Scattering
        game_scene.eevee.sss_samples          = imported_scene.eevee.sss_samples
        game_scene.eevee.sss_jitter_threshold = imported_scene.eevee.sss_jitter_threshold

        # Screen Space Reflection
        game_scene.eevee.use_ssr            = imported_scene.eevee.use_ssr
        game_scene.eevee.use_ssr_refraction = imported_scene.eevee.use_ssr_refraction
        game_scene.eevee.use_ssr_halfres    = imported_scene.eevee.use_ssr_halfres
        game_scene.eevee.ssr_quality        = imported_scene.eevee.ssr_quality
        game_scene.eevee.ssr_max_roughness  = imported_scene.eevee.ssr_max_roughness
        game_scene.eevee.ssr_thickness      = imported_scene.eevee.ssr_thickness
        game_scene.eevee.ssr_border_fade    = imported_scene.eevee.ssr_border_fade
        game_scene.eevee.ssr_firefly_fac    = imported_scene.eevee.ssr_firefly_fac

        # Motion Blur
        game_scene.eevee.use_motion_blur         = imported_scene.eevee.use_motion_blur
        game_scene.eevee.motion_blur_position    = imported_scene.eevee.motion_blur_position
        game_scene.eevee.motion_blur_shutter     = imported_scene.eevee.motion_blur_shutter
        game_scene.eevee.motion_blur_depth_scale = imported_scene.eevee.motion_blur_depth_scale
        game_scene.eevee.motion_blur_max         = imported_scene.eevee.motion_blur_max
        game_scene.eevee.motion_blur_steps       = imported_scene.eevee.motion_blur_steps

        # Volumetrics
        game_scene.eevee.volumetric_start               = imported_scene.eevee.volumetric_start
        game_scene.eevee.volumetric_end                 = imported_scene.eevee.volumetric_end
        game_scene.eevee.volumetric_tile_size           = imported_scene.eevee.volumetric_tile_size
        game_scene.eevee.volumetric_samples             = imported_scene.eevee.volumetric_samples
        game_scene.eevee.volumetric_sample_distribution = imported_scene.eevee.volumetric_sample_distribution
        game_scene.eevee.use_volumetric_lights          = imported_scene.eevee.use_volumetric_lights
        game_scene.eevee.volumetric_light_clamp         = imported_scene.eevee.volumetric_light_clamp
        game_scene.eevee.use_volumetric_shadows         = imported_scene.eevee.use_volumetric_shadows
        game_scene.eevee.volumetric_shadow_samples      = imported_scene.eevee.volumetric_shadow_samples

        # Performance
        game_scene.render.use_high_quality_normals = imported_scene.render.use_high_quality_normals

        # Curves
        game_scene.render.hair_type   = imported_scene.render.hair_type
        game_scene.render.hair_subdiv = imported_scene.render.hair_subdiv

        # Shadow
        game_scene.eevee.shadow_cube_size         = imported_scene.eevee.shadow_cascade_size
        game_scene.eevee.shadow_cascade_size      = imported_scene.eevee.shadow_cascade_size
        game_scene.eevee.use_shadow_high_bitdepth = imported_scene.eevee.use_shadow_high_bitdepth
        game_scene.eevee.use_soft_shadows         = imported_scene.eevee.use_soft_shadows
        game_scene.eevee.light_threshold          = imported_scene.eevee.light_threshold

        # Film
        game_scene.render.filter_size      = imported_scene.render.filter_size
        game_scene.render.film_transparent = imported_scene.render.film_transparent
        game_scene.eevee.use_overscan      = imported_scene.eevee.use_overscan
        game_scene.eevee.overscan_size     = imported_scene.eevee.overscan_size

        # Simplify

        game_scene.render.use_simplify                    = imported_scene.render.use_simplify
        game_scene.render.simplify_subdivision_render     = imported_scene.render.simplify_subdivision_render
        game_scene.render.simplify_child_particles_render = imported_scene.render.simplify_child_particles_render
        game_scene.render.simplify_shadows_render         = imported_scene.render.simplify_shadows_render
        game_scene.render.simplify_gpencil                = imported_scene.render.simplify_gpencil
        game_scene.render.simplify_gpencil_onplay         = imported_scene.render.simplify_gpencil_onplay
        game_scene.render.simplify_gpencil_view_fill      = imported_scene.render.simplify_gpencil_view_fill
        game_scene.render.simplify_gpencil_modifier       = imported_scene.render.simplify_gpencil_modifier
        game_scene.render.simplify_gpencil_shader_fx      = imported_scene.render.simplify_gpencil_shader_fx
        game_scene.render.simplify_gpencil_tint           = imported_scene.render.simplify_gpencil_tint
        game_scene.render.simplify_gpencil_antialiasing   = imported_scene.render.simplify_gpencil_antialiasing
        
        # Grease pencil
        game_scene.grease_pencil_settings.antialias_threshold = imported_scene.grease_pencil_settings.antialias_threshold
        
        # Freestyle
        game_scene.render.use_freestyle       = imported_scene.render.use_freestyle
        game_scene.render.line_thickness_mode = imported_scene.render.line_thickness_mode
        game_scene.render.line_thickness      = imported_scene.render.line_thickness
        
        game_scene.display_settings.display_device    = imported_scene.display_settings.display_device
        game_scene.view_settings.view_transform       = imported_scene.view_settings.view_transform
        game_scene.view_settings.look                 = imported_scene.view_settings.look
        game_scene.view_settings.exposure             = imported_scene.view_settings.exposure
        game_scene.view_settings.gamma                = imported_scene.view_settings.gamma
        game_scene.sequencer_colorspace_settings.name = imported_scene.sequencer_colorspace_settings.name
        