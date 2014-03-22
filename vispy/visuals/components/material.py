# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Material components are modular shader components used for modifying fragment
colors to change the visual's appearance.

These generally create a function in the fragment shader that accepts a vec4
color as its only argument and returns a modified vec4 color.
"""

from __future__ import division

import numpy as np

from ..visual import VisualComponent
from ..shaders import Function
from ... import gloo


class GridContourComponent(VisualComponent):
    """
    Draw grid lines across a surface.    
    """
    
    SHADERS = dict(
        frag_color="""
            vec4 $grid_contour(vec4 color) {
                if ( mod($pos.x, $spacing.x) < 0.005 ||
                    mod($pos.y, $spacing.y) < 0.005 || 
                    mod($pos.z, $spacing.z) < 0.005 ) {
                return color + 0.7 * (vec4(1,1,1,1) - color);
                }
                else {
                    return color;
                }
            }
        """,
        vert_post_hook="""
            void $grid_contour_support() {
                $output_pos = local_position();
            }
        """)
    
    def __init__(self, spacing):
        self.spacing = spacing
        
    @property
    def color(self):
        return self._color
    
    @color.setter
    def color(self, c):
        self._color = c
        
    def activate(self, program, mode):
        ff = self._funcs['frag_color']
        ff['pos'] = ('varying', 'vec4')
        ff['spacing'] = ('uniform', 'vec3', self.spacing)
        self._funcs['vert_post_hook']['output_pos'] = ff['pos']


class ShadingComponent(VisualComponent):
    """
    Phong reflection and shading material.    
    """
    
    SHADERS = dict(
        frag_color="""
            vec4 $shading(vec4 color) {
                vec3 norm = normalize($normal().xyz);
                vec3 light = normalize($light_direction.xyz);
                float p = dot(light, norm);
                p = (p < 0. ? 0. : p);
                vec4 diffuse = $light_color * p;
                diffuse.a = 1.0;
                p = dot(reflect(light, norm), vec3(0,0,1));
                if (p < 0.0) {
                    p = 0.0;
                }
                vec4 specular = $light_color * 5.0 * pow(p, 100.);
                return color * ($ambient + diffuse) + specular;
            }
        """)
    
    def __init__(self, normal_comp, lights, ambient=0.2):
        self.normal_comp = normal_comp
        self.lights = lights
        self.ambient = ambient
        
    def activate(self, program, mode):
        # Normals are generated by output of another component
        ff = self._funcs['frag_color']
        ff['normal'] = self.normal_comp.normal_shader()
        
        # TODO: add support for multiple lights
        ff['light_direction'] = ('uniform', 'vec4', tuple(self.lights[0][0][:3]) + (1,))
        ff['light_color'] = ('uniform', 'vec4', tuple(self.lights[0][1][:3]) + (1,))
        ff['ambient'] = ('uniform', 'float', self.ambient)
