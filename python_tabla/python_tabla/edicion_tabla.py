'''
Definición de funciones para editar los datos de las tablas, y poder
modificarlos en la base de datos a la que estamos conectados.

Created on 22 abr 2026

@author: pedro

'''

from .tabla import Tabla

class TablaEdicion(Tabla):
    
    def añadir_combo(self, columna, lista, actualizar, inicial=None):
        """
        Añadir un combo para poder editar los datos de la tabla. El combo
        aparece cuando el usuario selecciona una celda correspondeinte a la
        columna sobre la que se ha añadido el combo.
        
        Argumentos:
        - columna: columna de la tabla sobre la que se añade el combo.
        - lista: iterador, con la lista de elementos a añdir en el combo.
        - actualizar: función que se ejecuta una vez el usuario selecciona un
          elemento del combo. Si no selecciona ninguno (por ejemplo, pulsa
          escape, o bien hace click sobre otra parte de la tabla, no se
          ejecuta nada.
        - inicial: Si la celda en cuestión tiene datos antes de seleccionarla y
          y no coincide con uno de los textos de lista, sería el índice de lista
          que debe tomar el combo una vez desplegado.
        
        """
        pass