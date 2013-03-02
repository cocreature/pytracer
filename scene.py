import xml.etree.ElementTree as ET

import vector
import materials
import lights
import camera
import objects
import ray

import color


class Scene:
    ''' it’s a room … more or less
    '''
    def __init__(self, file_path):
        scene_xml = ET.parse(file_path)
        scene = scene_xml.getroot()
        self.materials = materials.parse(scene.findall('materials'))
        self.objects = objects.parse(scene.findall('objects'))
        self.lights = lights.parse(scene.findall('lights'))
        self.background = color.parse(scene.findall('background'))
        self.ambient_light = color.parse(scene.findall('ambient'))
        self.camera = camera.parse(scene.findall('camera'))

    def send_ray(self, r, recursion_level=4):
    #does it make sense to set the recursion level per ray?
        ''' sends a ray t
            :param Ray r: starpoint and direction
            :pram int recursion_level: how many light recursion
        '''
        t_min = float('inf')
        for o in self.objects:
        #find the closest object
            t, tmp_point, tmp_normal = o.intersects(r)
            if t < t_min:
                t_min = t
                hit = o
                point = tmp_point
                normal = tmp_normal
                #normalvector

        if hit:
            new_color = hit.material.ambient_color * self.ambient_light
            #a tiny base glow of everything
            for ls in self.lights:
            #check all ligths
                if ls.is_visible_from_point(point, normal, self.objects):
                #if the light is visibile from the point the ray hit
                    if normal * ls.light_direction(point) > 0:
                    #if there is still light
                        new_color += color.dot(hit.material.diffuse_color,
                                               ls.get_color(point) *
                                               vector.dot(normal,
                                                          ls.light_direction(point)))

                        lr = -(2 * vector.dot(normal,
                                              ls.light_direction(point) *
                                              normal -
                                              ls.light_direction(point)))

                        new_color += (hit.material.specular_color *
                                      ls.get_color(point) *
                                      lr *
                                      r.direction /
                                      (lr.length * r.direction.length) **
                                      hit.material.phong_specular_exponent)

            if recursion_level < 0:
                return new_color

            r2 = ray.Ray(point + 0.01 * normal, -(2 * (normal * r.direction) *
                                                  normal - r.direction))
            new_color += color.dot(hit.material.reflection_color,
                                   self.rend_ray(r2, recursion_level - 1))
            return new_color
        else:
            return self.background

    def getMaterialByName(self, strName):
        '''
            :param str strName: name of the wanted material
            :returns: a material with strName as name or non if not found
            :rtype: Material
        '''
        return self.materials.findall(strName)