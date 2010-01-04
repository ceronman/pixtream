# encoding:utf8
"""
Protocol spec generator
"""

import os
import sys

current_path = os.path.abspath(__file__)
current_path = os.path.dirname(current_path)
pixtream_path = os.path.join(current_path, '../../src')

sys.path.append(pixtream_path)

import string
import struct
import inspect

from pixtream.peer import specs

ENTRY_TPL = string.Template(r'''
\subsection{Mensaje \emph{$name}}
\label{subsec:mensaje_$lower_name}

$description

\begin{figure}[H]
\begin{center}
\begin{tabular}{$table_spec}
\toprule

    $struct_names \\

    $struct_sizes \\

    $struct_types \\

\bottomrule
\end{tabular}
\end{center}
\caption{Estructura del mensaje \emph{$name}}
\label{tab:structure_$lower_name}
\end{figure}

\begin{table}[H]
\begin{tabular}{p{0.2\textwidth} p{0.8\textwidth}}
\toprule
    \textbf{Campo} & \textbf{Descripción} \\
\midrule
    $field_descriptions
\bottomrule
\end{tabular}
\caption{Campos del mensaje \emph{$name}}
\label{tab:description_$lower_name}
\end{table}
''')

NAME_TPL = string.Template(r'\textbf{$name}')
SIZE_TPL = string.Template(r'\footnotesize{$size}')
TYPE_TPL = string.Template(r'\footnotesize{\emph{$type}}')

ID_TPL = string.Template(r"id = ``$id''")

COLUMN_SEP = ' &\n    '
ROW_SEP = ' \\\\\n    '
SPEC_SEP =  ' | '
SPEC_VALUE = 'l'

def generate_message_doc(message):

    def field_name(field):
        name =  field.name.replace('_', ' ')
        return NAME_TPL.substitute(name=name)

    def field_size(field):
        size = struct.calcsize(field.struct_string)

        if size == 1:
            size = '1 byte'
        else:
            size =  '{0} bytes'.format(size)
        return SIZE_TPL.substitute(size=size)

    def field_type(field):
        types_dict = {'s': 'string', 'I': 'unsigned int'}
        type = types_dict.get(field.struct_string[-1], 'unknown')
        return TYPE_TPL.substitute(type=type)

    m_id = ID_TPL.substitute(id = message.message_header)

    extra_fields = [specs.Field('I', 'lenght', "Length prefix of the field"),
                    specs.Field('s', m_id, 'Message Prefix Identification')]

    all_fields = extra_fields + message.fields

    if issubclass(message, specs.VariableLengthMessage):
        payload = specs.Field('s', 'payload', message.payload.doc)
        all_fields.append(payload)

    names = map(field_name, all_fields)
    sizes = map(field_size, all_fields)
    types = map(field_type, all_fields)

    struct_names = COLUMN_SEP.join(names)
    struct_sizes = COLUMN_SEP.join(sizes)
    struct_types = COLUMN_SEP.join(types)

    table_spec = SPEC_SEP.join([SPEC_VALUE] * len(all_fields))

    name = message.__name__.replace('Message', '')
    lower_name = name.lower()
    description = message.__doc__.strip()

    def field_name_description(field):
        return field.name.replace('_', ' ') + COLUMN_SEP + field.doc + ROW_SEP

    descriptions = map(field_name_description, all_fields)

    field_descriptions = ''.join(descriptions)

    return ENTRY_TPL.substitute(name = name,
                                lower_name = lower_name,
                                description = description,
                                table_spec = table_spec,
                                struct_names = struct_names,
                                struct_sizes = struct_sizes,
                                struct_types = struct_types,
                                field_descriptions = field_descriptions)

if __name__ == '__main__':
    messages = [c for n, c in inspect.getmembers(specs, inspect.isclass)
                if issubclass(c, specs.Message)
                and c not in (specs.Message,
                              specs.FixedLengthMessage,
                              specs.VariableLengthMessage)]

    messages.sort(key=lambda m: inspect.getsourcelines(m)[1])

    for message in messages:
        print generate_message_doc(message)
