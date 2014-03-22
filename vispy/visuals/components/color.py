# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Color components are modular shader components used for retrieving or
generating fragment colors.

These components create a function in the fragment shader that accepts no 
arguments and returns a vec4 color.
"""

from __future__ import division

import numpy as np

from ..visual import VisualComponent
from ..shaders import Function
from ... import gloo


class UniformColorComponent(VisualComponent):
    """
    Generates a uniform color for all vertexes.
    """
    
    SHADERS = dict(
        frag_color="""
            vec4 $colorInput() {
                return $rgba;
            }
        """)
    
    def __init__(self, color=(1,1,1,1)):
        self._color = color
        
    @property
    def color(self):
        return self._color
    
    @color.setter
    def color(self, c):
        self._color = c
        
    def activate(self, program, mode):
        self._funcs['frag_color']['rgba'] = ('uniform', 'vec4', np.array(self._color))


class VertexColorComponent(VisualComponent):
    """
    Reads color in from (N,4) array or vertex buffer.
    """
    
    SHADERS = dict(
        frag_color="""
            vec4 $colorInput() {
                return $rgba;
            }
        """,
        vert_post_hook="""
            void $colorInputSupport() {
                $output_color = $input_color;
            }
        """
        )
    
    def __init__(self, color=None):
        self._color = color
        self._vbo = None
        
    @property
    def color(self):
        return self._color
    
    @color.setter
    def color(self, c):
        self._color = c
        
    @property
    def vbo(self):
        if self._vbo is None:
            self._vbo = gloo.VertexBuffer(self._color)
        return self._vbo
        
    def activate(self, program, mode):
        ff = self._funcs['frag_color']
        ff['rgba'] = ('varying', 'vec4')   
        
        vf = self._funcs['vert_post_hook']
        vf['output_color'] = ff['rgba']
        vf['input_color'] = ('attribute', 'vec4', self.vbo)

