#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymel.core as pm
import maya.cmds as mc
import logging

# logger = logging.getLogger(__file__)
# logger.setLevel(logging.DEBUG)

# 3 classes, la 1ra ModuleBase
class SelectionException(Exception):
    pass

class ModuleBase():
    def __init__(self):
        # create all the needed nodes
        self.create_nodes()
        # connect all out nodes
        self.connect_nodes()
        # set all attributes
        self.set_attrs()

    def create_nodes(self):
        pass

    def connect_nodes(self):
        pass

    def set_attrs(self):
        pass


class SurfaceForRivet(ModuleBase):
    def __init__(self, selection):
        self.sel = selection

        # check if we have selected the right amount of edges or a face
        if len(selection) == 1 and isinstance(selection[0], pm.MeshFace):
            # si la seleccion es una cara pillamos sus edges
            self.edges_indexes = self.convert_face_to_edges(selection[0])

        elif (len(selection) == 2 and isinstance(selection[0], pm.MeshEdge)):
            self.edges_indexes = [selection[0].indices()[0], selection[1].indices()[0]]
            print(self.edges_indexes)

        else:
            raise SelectionException('No valid selection! Please make sure that you select either a face or two mesh edges')

        self._in_mesh = selection[0].node()

        # logger.info("indexes of edges to process: {}".format(edges_indexes))

        # EL SUPER LO METEMOS AL FINAL DEL INIT PARA TENER YA TODA LA INFO PREPARADA ANTES DE
        # LLAMAR LA FUNCION
        super(SurfaceForRivet, self).__init__()

    def convert_face_to_edges(self, face):
        # esta siguiente linea devuelve primero el face, despues el num de faces y despues los edges.
        # Solo queremos coger los edges asi que hacemos un split y pillamos [-4:]
        # also no queremos las 4 caras, solo queremos 2 para hacer el loft, asi que
        # hacemos un enumerate que solo nos devuelva si es multiple de 2 (para coger solo las poses 1 y 3)
        return [int(i) for n,i in enumerate(pm.polyInfo(pm.selected()[0], faceToEdge = True)[0].split()[-4:]) if n%2]
        # si quisiesemos los impares podriamos poner if not y ya

    def create_nodes(self):
        # vamos a convertir el polygon edges to curve para poder crear el loft
        self.node = {
            "mesh_edge_node_01": pm.createNode("curveFromMeshEdge"),
            "mesh_edge_node_02": pm.createNode("curveFromMeshEdge"),
            "loft" : pm.createNode("loft")
        }

    def setAttrs(self):
        # IHI ATTR
        # La lista de inputs y outputs de un nodo se enseña en el attribute editor.
        # Esa lista puede llegar a ser relarga así que hay un atributo llamado
        # IS HISTORICALLY INTERESTING que permite decidir si aparece o no en esa lista
        # booleano true o false
        self.node["mesh_edge_node_01"].ihi.set(False)
        self.node["mesh_edge_node_02"].ihi.set(False)
        self.node["mesh_edge_node_01"].edgeIndex[0].set(self.edges_indexes[0])
        self.node["mesh_edge_node_02"].edgeIndex[0].set(self.edges_indexes[1])

        # seteamos todos los atributos que vaya a poder necesitar nuestro loft
        self.node["loft"].inputCurve.set.size(size=2)
        self.node["loft"].uniform.set(True)
        self.node["loft"].sectionSpans.et(3)
        # poniendo el caching ira mucho ma rapido al procearlo para rigging
        self.node["loft"].caching.set(True)

    def connect_nodes(self):
        self._in_mesh.worldMesh >> self.node["mesh_edge_node_01"].inputMesh
        self._in_mesh.worldMesh >> self.node["mesh_edge_node_02"].inputMesh

        self.node["mesh_edge_node_01"].outputCurve >> self.node["loft"].inputCurve[0]
        self.node["mesh_edge_node_02"].outputCurve >> self.node["loft"].inputCurve[1]

my_surface = SurfaceForRivet(pm.selected())

