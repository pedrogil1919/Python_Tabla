'''
Definición de funciones para editar los datos de las tablas, y poder
modificarlos en la base de datos a la que estamos conectados.

Created on 22 abr 2026

@author: pedro

'''

from functools import partial
from tkinter import ttk

from .tabla import Tabla


class ElementoCombo():
    """
    Para edición mediante combo, formato con el que pasar cada uno de los
    elementos de la lista desplegable del combo.

    """

    def __init__(self, codigo, texto=None, seleccionado=False):
        """
        Argumentos:
        - codigo: Código (ID) de la base de datos del elemento.
        - texto: Texto con el que se identifica el elemento. Si el código
          coincide con texto, pasar este valor a None
        - seleccionado: Indica si este elemento es el que debe aparecer
          seleccionado al desplegar el combo. Si en la lista de elementos
          ningún elemento tiene este valor a True, el combo se despliega sin
          ningún elemento seleccionado. Si tiene más de uno a True, se elige
          el último elemento de todos.

        """
        self.__codigo = codigo
        self.__texto = texto
        self.__seleccionado = seleccionado

    def get_codigo(self):
        return self.__codigo

    def get_texto(self):
        return self.__codigo if self.__texto is None else self.__texto

    def get_seleccionado(self):
        return self.__seleccionado
    
    def set_seleccionado(self, valor):
        self.__seleccionado = valor

    codigo = property(get_codigo, None, None, None)
    texto = property(get_texto, None, None, None)
    seleccionado = property(get_seleccionado, set_seleccionado, None, None)

###############################################################################


class TablaEdicion(Tabla):

    def __init__(self, *arg, **kwargs):
        """
        constructor. Pasamos los argumentos directamente a la clase principal

        """
        # Variable donde guardaremos qué columnas deben mostrar un combo al
        # seleccionarlo el usuario, junto con las funciones necesarias para
        # rellenarlo y actualizar los datos una vez selecionada una opción.
        self.__combos = {}
        # Para los combos, guardamos el valor inicial del combo al desplegar
        # la lista, ya que, en caso de pulsar escape, o error al guardar,
        # debemos poner el combo en su valor inicial.
        self.__valor_inicial_combo = None
        # Similar, pero para controles tipo Entry (no implementado)
        self.__texto = {}
        # Guardamos la referencia al útlimo control activo. Es necesario para
        # eliminarlo una vez finalizamos la edición, y para acceder a sus
        # eventos y propiedades durante la edición.
        self.__control_activo = None
        # Variable necesaria para poder desactivar el último control activo
        # una vez el control pierde el foco.
        self.__etiqueta_activa = None
        # Guardamos la información de pack, para que al volver a añadir la
        # etiqueta, conserve la misma geometría.
        self.__pack_info_etiqueta = None

        super().__init__(*arg, **kwargs)

    def añadir_fila(self, fila, valores):
        """
        Por cada fila que se añade, hay que añadir todos los eventos de edición
        que se hayan añadido en la configuración de la tabla.

        """
        # Añadir los datos de la fila.
        super().añadir_fila(fila, valores)
        # Para aquellas columnas que no tengan combo asignado, le asignamos el
        # evento de eliminar el combo activo. Esto es necesario por si el
        # usuario, una vez activa un combo, quiere desactivarlo pulsando sobre
        # otra celda de la tabla.
        for control in self._Tabla__controles[fila]['L'].values():
            control.bind("<Button-1>", self.__eliminar_control_activo)
            
        # Y por otro lado, añadimos a las etiquetas de las columnas que tienen
        # combo asociado el evento para añadirlo en caso de que el usuario
        # seleccione dicha celda.
        for columna, valor in self.__combos.items():
            self._Tabla__controles[fila]['L'][columna].bind(
                valor["evento"], partial(self.__sustituir_combo, fila, columna))            

    def añadir_combo(self, evento, columna, lista, actualizar):
        """
        Añadir un combo para poder editar los datos de la tabla. El combo
        aparece cuando el usuario selecciona una celda correspondeinte a la
        columna sobre la que se ha añadido el combo.

        Argumentos:
        - evento: tipo de evento al que hay que atender:
          - "<Button-1>"
          - "<Double-Button-1>"
          - ...
        - columna: columna de la tabla sobre la que se añade el combo.
        - lista: lista de elementos a mostrar en el desplegable del combo.
          Puede ser una lista de elementos, o bien puede ser un generador. En
          este último caso, el generador deberá aceptar como arguemento, un
          entero correspondiente a la fila seleccionada. Los elementos de esta
          lista deben ser del tipo ElementoCombo().
        - actualizar: función que se ejecuta una vez el usuario selecciona un
          elemento del combo. Si no selecciona ninguno (por ejemplo, pulsa
          escape, o bien hace click sobre otra parte de la tabla, no se
          ejecuta nada).  Toma como argumentos la fila en edición, y el código
          de la opción seleccionada. Devuelve True si la actualización fue
          correcta, y False si fue incorrecta, y hay que dejar el combo en su
          posición inicial.

        """
        # Guardamos las funciones para obtener la lista de elementos del combo
        # y la función para actualizar los datos una vez el usuario selecciona
        # una opción.
        self.__combos[columna] = {"evento": evento, 
                                  "lista": lista, 
                                  "actualizar": actualizar}

        # Configuramos el evento en todas las celdas de esta columna.
        for fila, controles in self._Tabla__controles.items():
            controles['L'][columna].bind(
                evento, partial(self.__sustituir_combo, fila, columna))

    def __sustituir_combo(self, fila, columna, evento=None):
        """
        Función para sustituir la etiqueta de la celda por un combobox.

        """
        # Eliminaos el útlimo control activo, si huviera alguno.
        self.__eliminar_control_activo()
        # Eliminamos la etiqueta actual, y la sustituimos por un combo.
        self.__etiqueta_activa = self._Tabla__controles[fila]['L'][columna]
        # Guardamos la configuración geométrica de la etiqueta, para que al
        # volver a hacerla aparecer, quede igual que antes de la edición.
        self.__pack_info_etiqueta = self.__etiqueta_activa.pack_info()
        # Hacemos desaparece la etiqueta.
        self.__etiqueta_activa.pack_forget()
        # A partir de aquí comienza la configuración del combobox. En primer
        # lugar, obtenemos los elementos a mostrar en la lista.
        lista = self.__combos[columna]["lista"]
        if callable(lista):
            # Caso de que la lista se obtenga de un generador.
            self.__valores_combo = [v for v in lista(fila)]
        else:
            # Caso de la que lista sea una lista de python.
            self.__valores_combo = lista

        # Creamos la lista de textos para mostrar en el desplegable.
        valores = []
        # Variable para obtener el elemento inicial que estará seleccionado en
        # el combo al desplegarlo. Recordemos que el valor inicial viene
        # indicado en la variable "seleccionado" de la clase ElementoCombo.
        inicial = None
        for indice, item in enumerate(self.__valores_combo):
            # Añadimos el texto de la etiqueta a la lista de textos.
            valores.append(item.texto)
            if item.seleccionado:
                # Y si este es el elemento inicial, nos quedamos con su indice.
                # Notese que si hay más de un elemento inicial, nos quedaremos
                # con el último de todos.
                inicial = indice

        # Actualizamos el tipo de fuente para el desplegable.
        # NOTA: Tkinter no permite configurar esto para cada combobox, sino que
        # se fija el mismo para todos los combos de la aplicación.
        self._Tabla__controles[fila]['F'][columna].option_add(
            "*TCombobox*Listbox.font", self._Tabla__fuente_filas)
        # Finalmente creamos el combobox con la lista de valores obtenida
        # anteriormente.
        self.__control_activo = ttk.Combobox(
            self._Tabla__controles[fila]['F'][columna], values=valores,
            font=self._Tabla__fuente_filas, state="readonly")
        if inicial is not None:
            # Guardamos el valor inicial, por si tenemos que vevolverlo a su
            # valor inicial en caso de error.
            self.__valor_inicial_combo = inicial
            # Marcamos en el combo el elemento que debe aparecer seleccionado
            # al desplegar la lista del combo.
            self.__control_activo.current(self.__valor_inicial_combo)
        else:
            self.__valor_inicial_combo = None
        # Función que atiende al evento de selección. El evento se distara
        # tanto si se selecciona con el ratón o con enter del teclado.
        self.__control_activo.bind(
            "<<ComboboxSelected>>",
            partial(self.__seleccion_combo, fila, columna))
        # Añadimos el combo con la misma configuración geométrica que la
        # etiqueta de la celda.
        self.__control_activo.pack(self.__pack_info_etiqueta)
        # Desactivamos el combo cuando el usuario pulse Escape..
        self.__control_activo.bind(
            "<Escape>", self.__eliminar_control_activo)
        self.__control_activo.bind(
            "<FocusOut>", self.__perdida_foco_combo)
        # Y damos el foco al combo,
        self.__control_activo.focus_set()

    def __seleccion_combo(self, fila, columna, evento=None):
        """
        Actualizar en el caso de que el usuario seleccione una opción.

        """
        # Cogemos el índice del elemento seleccionado.
        indice = self.__control_activo.current()
        # y lo traducimos al índice correspondiente.
        codigo = self.__valores_combo[indice].codigo
        # Coger la función de actualización que nos pasó el cliente.
        actualizar = self.__combos[columna]["actualizar"]
        # Y realizamos la actualizacion.
        if not actualizar(fila, codigo):
            # En caso de error al actualizar, dejamos el combo en el valor
            # inicial.
            self.__control_activo.current(self.__valor_inicial_combo)
        else:
            # En el caso de que al modificar el valor del campo, la lista de
            # elementos del combo deba cambiarse, lo que hacemos es eliminar
            # el combo actual y sustituirlo por uno nuevo. En el caso de que
            # no cambie, esta acción no afecta.
            self.__sustituir_combo(fila, columna, evento)

    def __eliminar_control_activo(self, evento=None):
        # Eliminar el último control que hemos estado editando, y lo sustituimos
        # por la etiqueta de dicha celda.
        if self.__control_activo is not None:
            self.__control_activo.destroy()
        if self.__etiqueta_activa is not None:
            self.__etiqueta_activa.pack(**self.__pack_info_etiqueta)
            self.__etiqueta_activa = None

    def __perdida_foco_combo(self, evento=None):
        """
        Chequea si la pérdida del foco del combobox es debido a que se ha
        desplegado la lista de opciones (así funciona el combobox de tkinter)
        o bien porque se ha seleccionado otro control dentro de la aplicación.

        """
        # Como no es posible determinar si la pérdida del foco es porque se ha
        # desplegado la lista del combo, o bien porque hemos seleccionado otro
        # control, tenemos que lanzar una función de chequeo, dando unos 20 ms
        # de margen para que el control pueda tomar el foco de forma efectiva.
        evento.widget.after(20, self.__chequear_cambio_foco, evento.widget)

    def __chequear_cambio_foco(self, combobox):
        # Función principal para chequear la pérdida del foco.
        try:
            # Coprobamos si podemos obtener el foco del combobox.
            __ = combobox.focus_get()
        except KeyError:
            # Si no podemos, es porque el foco lo tiene una ventana distinta a
            # la que contiene el combobox, que en un caso normal, se corresponde
            # con el TopLevel de la lista despleglable del combo. En este caso,
            # determinamos que no hay pérdida de foco, sino que hemos desplegado
            # la lista.
            return
        else:
            # En el resto de casos, es porque el foco lo tiene ahora un control
            # distinto de la misma aplicación, por lo que es una pérdida real
            # del foco.
            self.__eliminar_control_activo()
        """
        if foco_actual is None:
            # El foco se fue fuera de la aplicación.
            print("El foco se fue fuera de la aplicación.")
        elif foco_actual.winfo_toplevel() != combobox.winfo_toplevel():
            # El widget con foco está en un Toplevel diferente (la lista desplegada)
            print("La pérdida de foco fue por DESPLEGAR la lista")
        else:
            print("La pérdida de foco fue por SELECCIONAR otro control")
        """
