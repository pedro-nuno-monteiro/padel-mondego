import psycopg2
import psycopg2.extras
import os
import time
from datetime import datetime, timedelta, date
from prettytable import PrettyTable

def main():
    os.system('cls')

    # conexão com base de dados
    connection = database_connection()
    if not connection:
        print("Erro na conexão - a sair do programa")
        return

    atualiza_campos(connection)

    tipo_user = None
    opcao = 1
    while opcao > 0 or opcao < 3:
        opcao = menu()
        if opcao == 1:

            # encriptar passwords :)
            utilizador = login(connection)

            # definir o tipo de utilizador
            tipo_user = tipo_utilizador(connection, utilizador)

        elif opcao == 2:
            register(connection)

        elif opcao == 3:
            sair()
            break
        
        if tipo_user == 'admin' or tipo_user == 'super_admin':
            menu_admin(connection, utilizador, tipo_user)
        else:
            menu_cliente(connection, utilizador)

    print("adeus")

# ------------------------------------
def menu_admin(connection, utilizador, tipo_user):
    
    cursor = connection.cursor(cursor_factory = psycopg2.extras.DictCursor)

    print(" ***** Menu Admin *****\n *")
    print(" * 1 - Alterar Reservas")
    print(" * 2 - Alterar Preços")
    print(" * 3 - Estatísticas")
    print(" * 4 - Mensagem Geral")
    print(" * 5 - Mensagem Privada")

    opcao = 1 
    while opcao > 0 or opcao < 7:
        opcao = apresentar_menu_admin(tipo_user)

        if opcao == 1:
            alterar_reservas_menu(connection)
        
        elif opcao == 2:
            alterar_precos(connection)

        elif opcao == 3:
            print("estatísticas")

        elif opcao == 4:
            print("mensagem geral")
        
        elif opcao == 5:
            print("mensagem privada")

        elif opcao == 6:
            os.system('cls')
            return None

# ------------------------------------
def alterar_precos(connection):

    cursor = connection.cursor(cursor_factory = psycopg2.extras.DictCursor)
    os.system('cls')
    print(" ***** Alterar Preços *****\n *\n")

    fetch_precos = """
        SELECT *
        FROM price
        ORDER BY ativo DESC, tipo_dia, horario DESC, data_alteracao
    """

    cursor.execute(fetch_precos)
    precos_totais = cursor.fetchall()
    precos_atuais = []
    table = PrettyTable()
    table.field_names = ["#", "Tipo Dia", "Horário", "Data Alteração", "Preço Antigo", "Preço Atual"]
    for i, preco in enumerate(precos_totais, start = 1):
        if preco['ativo']:
            precos_atuais.append(preco)
            apresentar_preco_antigo = f"{preco['valor_antigo']} €"
            apresentar_preco = f"{preco['preco_atual']} €"
            table.add_row([i, preco['tipo_dia'], preco['horario'], preco['data_alteracao'].strftime("%d/%m"), apresentar_preco_antigo, apresentar_preco])

    print(table)

    print(" \n * 4. Ver histórico total")
    print(" * 5. Regressar")

    opcao = 0
    regressar = False
    while opcao < 1 or opcao > 5:
        opcao = int(input(" * \n * Escolha uma opção -> "))

        if opcao < 4:
            preco_a_alterar = precos_atuais[opcao - 1]
            break

        elif opcao == 4:
            
            os.system('cls')
            print(" ***** Histórico de Preços *****\n ")
            table_2 = PrettyTable()
            table_2.field_names = ["Tipo Dia", "Horário", "Data Alteração", "Preço Antigo", "Preço Atual", "Ativo"]
            count_ativo = 0
            for preco in precos_totais:
                if preco['ativo']:
                    ativo = "Sim"
                    count_ativo += 1
                else:
                    ativo = "Não"
                apresentar_preco_antigo = f"{preco['valor_antigo']} €"
                apresentar_preco = f"{preco['preco_atual']} €"
                if count_ativo == 3:
                    count_ativo = 0
                    table_2.add_row([preco['tipo_dia'], preco['horario'],
                                preco['data_alteracao'].strftime("%d/%m"), apresentar_preco_antigo, apresentar_preco, ativo], divider = True)
                else:
                    table_2.add_row([preco['tipo_dia'], preco['horario'],
                                preco['data_alteracao'].strftime("%d/%m"), apresentar_preco_antigo, apresentar_preco, ativo])

            print(table_2)
            regressar = True
            input("\n Regressar - Enter")
            
        elif opcao == 5:
            regressar = True
            break

    if not regressar:
        os.system('cls')
        print(" ***** Alterar Preço *****\n *")
        print(" * Preço a alterar:\n *")

        table_3 = PrettyTable()
        table_3.field_names = ["Tipo Dia", "Horário", "Data Alteração", "Preço Antigo", "Preço Atual"]
        apresentar_preco = f"{preco_a_alterar['preco_atual']} €"
        apresentar_preco_antigo = f"{preco_a_alterar['valor_antigo']} €"
        table_3.add_row([preco_a_alterar['tipo_dia'], preco_a_alterar['horario'],
                        preco_a_alterar['data_alteracao'].strftime("%d/%m"), apresentar_preco_antigo, apresentar_preco])

        print(table_3)

        novo_preco = preco_a_alterar['preco_atual']
        while novo_preco < 0 or novo_preco == preco_a_alterar['preco_atual']:
            novo_preco = int(input("\n * Indique o novo preço -> "))

            if novo_preco == preco_a_alterar['preco_atual']:
                print(" * \n * ATENÇÃO -> Preço igual ao anterior! * ")

        # acrescenta novo preco
        proximo_id_custo = max([preco['id_custo'] for preco in precos_totais]) + 1
        data_alteracao = date(year = 2024, month = 4, day = 16)
        atualizar_preco = """
            INSERT INTO price (id_custo, tipo_dia, horario, data_alteracao, ativo, valor_antigo, preco_atual)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(atualizar_preco, (proximo_id_custo, preco_a_alterar['tipo_dia'], preco_a_alterar['horario'],
                                        data_alteracao, True, preco_a_alterar['preco_atual'], novo_preco))
        connection.commit()

        # altera o anterior
        alterar_preco = """
            UPDATE price
            SET ativo = False
            WHERE id_custo = %s
        """
        cursor.execute(alterar_preco, (preco_a_alterar['id_custo'],))
        connection.commit()

        print(" * Preço atualizado com sucesso!")
        input(" * \n * Regressar - Enter")

# ------------------------------------
def alterar_reservas_menu(connection):

    cursor = connection.cursor(cursor_factory = psycopg2.extras.DictCursor)

    data_teste = datetime(year = 2024, month = 4, day = 16, hour = 14, minute = 00, second = 00)

    fetch_reservas_futuras = """
        SELECT 
            u.email, u.nome, r.id_reserva, r.horario AS r_horario, 
            r.estado, r.campo_id_campo, p.tipo_dia, p.horario AS p_horario, p.preco_atual
        FROM 
            reserva as r, price as p, utilizador as u
        WHERE 
            r.horario >= %s AND u.email = r.cliente_utilizador_email AND r.price_id_custo = p.id_custo
        ORDER BY
            u.email, r.horario, r.campo_id_campo
    """
    
    #cursor.execute(fetch_reservas_futuras, (datetime.now(),))
    cursor.execute(fetch_reservas_futuras, (data_teste,))
    reservas_futuras = cursor.fetchall()

    os.system("cls")
    print(" ***** Alterar Reservas *****\n *")
    print(" * Neste menu é possível:")
    print(" * * Alterar reservas")
    print(" * * Cancelar reservas\n ")

    table = PrettyTable()
    table.field_names = ["#", "Cliente", "Email", "Horário", "Campo", "Estado"]

    current_user = reservas_futuras[0]['email']
    for i, reserva_futura in enumerate(reservas_futuras, start = 1):

        if i + 1 < len(reservas_futuras):
            next_user = reservas_futuras[i]['email']
            if next_user != current_user:
                table.add_row([i, reserva_futura['nome'], reserva_futura['email'],
                        reserva_futura['r_horario'].strftime("%d/%m, %Hh%M"), reserva_futura['campo_id_campo'],
                        reserva_futura['estado']], divider = True)
            else:
                table.add_row([i, reserva_futura['nome'], reserva_futura['email'],
                        reserva_futura['r_horario'].strftime("%d/%m, %Hh%M"), reserva_futura['campo_id_campo'],
                        reserva_futura['estado']])
        else:
            table.add_row([i, reserva_futura['nome'], reserva_futura['email'],
                        reserva_futura['r_horario'].strftime("%d/%m, %Hh%M"), reserva_futura['campo_id_campo'],
                        reserva_futura['estado']])

    print(table)

    print(f"\n * {len(reservas_futuras) + 1}. Regressar")

    opcao = 0
    regressar = False
    while opcao < 1 or opcao > len(reservas_futuras) + 1:
        opcao = int(input(" * \n * Escolha uma reserva -> "))

        if opcao == len(reservas_futuras) + 1:
            regressar = True
            break

        elif opcao < len(reservas_futuras) + 1:
            print(" * \n * 1 - Alterar Reserva")
            print(" * 2 - Cancelar Reserva")
            print(" * 3 - Regressar\n * ")

            opcao_admin = 0
            while opcao_admin < 1 or opcao_admin > 3:
                opcao_admin = int(input(" * Escolha uma opção -> "))
                
                if opcao_admin == 3:
                    regressar = True
                    break

            reserva_a_alterar = reservas_futuras[opcao - 1]

    if not regressar:
        
        # alterar reserva
        if opcao_admin == 1:
            alterar_reservas(connection, reserva_a_alterar, reservas_futuras)

        elif opcao_admin == 2:
            
            ja_cancelado = False
            if reserva_a_alterar['estado'] == 'Cancelado':
                print(" * \n * ATENÇÃO -> Reserva já cancelada! * ")
                input(" * \n * Regressar - Enter")
                ja_cancelado = True

            if not ja_cancelado:
                cancelar_reserva = """
                    UPDATE reserva
                    SET estado = 'Cancelado'
                    WHERE id_reserva = %s
                """
                cursor.execute(cancelar_reserva, (reserva_a_alterar['id_reserva'],))
                connection.commit()

                print(" * Reserva cancelada com sucesso!")
                input(" * \n * Regressar - Enter")

# ------------------------------------
def alterar_reservas(connection, reserva_a_alterar, reservas_futuras):
    
    cursor = connection.cursor(cursor_factory = psycopg2.extras.DictCursor)

    os.system("cls")
    print(" ***** Alterar Reserva *****\n *")
    print(" * Reserva a alterar:\n")
    
    table_2 = PrettyTable()
    table_2.field_names = ["Cliente", "Email", "Horário", "Situação", "Preço", "Campo", "Estado"]
    apresentar_situacao = f"{reserva_a_alterar['tipo_dia']}, {reserva_a_alterar['p_horario']}"
    apresentar_preco = f"{reserva_a_alterar['preco_atual']} €"
    table_2.add_row([reserva_a_alterar['nome'], reserva_a_alterar['email'],
                reserva_a_alterar['r_horario'].strftime("%d/%m, %Hh%M"), apresentar_situacao,
                apresentar_preco, reserva_a_alterar['campo_id_campo'], reserva_a_alterar['estado']])
    print(table_2)

    print("\n * 1. Alterar Campo")
    print(" * 2. Alterar Dia")  
    print(" * 3. Alterar Hora")
    print(" * 4. Alterar Estado")

    opcao_alterar = 0
    while opcao_alterar < 1 or opcao_alterar > 4:
        opcao_alterar = int(input(" * \n * Escolha uma opção -> "))

    # alterar campo
    if opcao_alterar == 1:
        novo_campo = reserva_a_alterar['campo_id_campo']

        outros_campos = []
        table_3 = PrettyTable()
        table_3.field_names = ["Cliente", "Email", "Horário", "Situação", "Preço", "Campo", "Estado"]
        for reserva_futura in reservas_futuras:
            if (reserva_futura['campo_id_campo'] != reserva_a_alterar['campo_id_campo']) and reserva_futura['r_horario'] == reserva_a_alterar['r_horario']:
                outros_campos.append(reserva_futura['campo_id_campo'])
                apresentar_situacao = f"{reserva_futura['tipo_dia']}, {reserva_futura['p_horario']}"
                apresentar_preco = f"{reserva_futura['preco_atual']} €"
                table_3.add_row([reserva_futura['nome'], reserva_futura['email'],
                            reserva_futura['r_horario'].strftime("%d/%m, %Hh%M"), apresentar_situacao,
                            apresentar_preco, reserva_futura['campo_id_campo'], reserva_futura['estado']], divider = True)
        
        if len(outros_campos) > 0:
            print(" *\n * Reservas noutros campos, à mesma hora:\n ")
            print(table_3)
        
        else:
            print(" * \n * Não há reservas noutros campos, à mesma hora * ")

        opcao_invalida = True
        while novo_campo < 1 or novo_campo > 3 or opcao_invalida:

            if len(outros_campos) == 2:
                print(" * Todos os restantes campos estão ocupados")

            else:
                novo_campo = int(input("\n * Indique o novo campo: "))

            if novo_campo == reserva_a_alterar['campo_id_campo']:
                print(" * \n * ATENÇÃO -> Campo igual ao anterior!\n * ")
            elif novo_campo in outros_campos:
                print(" * \n * ATENÇÃO -> Campo já reservado! * ")
            else:
                opcao_invalida = False

        # atualizar a reserva selecionada
        atualizar_reserva = """
            UPDATE reserva
            SET campo_id_campo = %s
            WHERE cliente_utilizador_email = %s AND horario = %s AND estado = %s
        """
        cursor.execute(atualizar_reserva, (novo_campo, reserva_a_alterar['email'], reserva_a_alterar['r_horario'], reserva_a_alterar['estado']))
        connection.commit()

        print(" * Campo atualizado!")
        input(" * \n * Regressar - Enter")

    # alterar dia
    elif opcao_alterar == 2:
        novo_dia = reserva_a_alterar['r_horario'].day

        while novo_dia < novo_dia or novo_dia > (novo_dia + 7) or novo_dia == reserva_a_alterar['r_horario'].day:
            novo_dia = int(input(" * Indique o novo dia: "))
            
            if novo_dia == reserva_a_alterar['r_horario'].day:
                print(" * \n * ATENÇÃO -> Dia igual ao anterior! * ")
    
    # alterar hora
    elif opcao_alterar == 3:
        nova_hora = reserva_a_alterar['r_horario'].strftime("%Hh%M")
        horarios_semana = ["15h00", "16h30", "18h00", "19h30", "21h00", "22h30"]
        
        for i in range(1, 7):
            print(f" * {i}. {horarios_semana[i - 1]}")
        
        while nova_hora not in horarios_semana:
            opcao_hora = input(" * Indique a nova hora: ")
            nova_hora = horarios_semana[opcao_hora - 1]

            if nova_hora not in horarios_semana:
                print(" * \n * ATENÇÃO -> Hora inválida! * ")

    # alterar estado
    elif opcao_alterar == 4:
        novo_estado = reserva_a_alterar['estado']
        estados = ["Reservado", "Cancelado", "Finalizado", "Em Espera", "Em Espera Cancelado", "Alterado Reservado", "Alterado Finalizado"]

        for i in range(1, 7):
            print(f" * {i}. {estados[i - 1]}")
        
        while novo_estado not in estados or novo_estado == reserva_a_alterar['estado']:
            opcao_estado = input(" * Indique o novo estado: ")
            novo_estado = estados[opcao_estado - 1]

            if novo_estado == reserva_a_alterar['estado']:
                print(" * \n * ATENÇÃO -> Estado igual ao anterior! * ")
    
    # atualizar a reserva selecionada
    atualizar_reserva = """
        UPDATE reserva
        SET %s = %s,
        WHERE 
    """
# ------------------------------------
def menu_cliente(connection, utilizador):

    cursor = connection.cursor(cursor_factory = psycopg2.extras.DictCursor)

    opcao = 1
    while opcao > 0 or opcao < 5:
        opcao = apresentar_menu_cliente()

        if opcao == 1:

            os.system('cls')
            print(" ***** Informações do clube Padel Mondego *****\n *")
            print(" * Lorem ipsum dolor sit amet, consectetur adipiscing elit.\n * Nunc cursus porttitor nisi a venenatis. \n * Mauris elementum tincidunt nisi eu consequat.\n * Cras tristique libero cursus sem eleifend facilisis.\n * In hac habitasse platea dictumst.")
            print(" \n\n ")
            print(" ***** Perfil do Cliente *****\n *")
            print(" * Nome: ", utilizador['nome'])
            print(" * Email: ", utilizador['email'])
            print(" * NIF: ", utilizador['nif'])
            print(" * Telemóvel: ", utilizador['numero_telefone'])
            input(" * \n * Regressar - Enter")

        elif opcao == 2:
            efetuar_reserva(connection, utilizador)

        elif opcao == 3:
            reservas_atuais(connection, utilizador)

        elif opcao == 4:
            historico_reservas(connection, utilizador)

        elif opcao == 5:
            os.system('cls')
            return None

# ------------------------------------
def efetuar_reserva(connection, utilizador):

    cursor = connection.cursor(cursor_factory = psycopg2.extras.DictCursor)

    # update das datas das reservas para teste!
    #custom_date = datetime(year = 2024, month = 4, day = 16)
    #update_query = f"UPDATE reserva SET horario = '{custom_date.strftime('%Y-%m-%d')}'"
    #cursor.execute(update_query)
    #connection.commit()

    date = datetime(year = 2024, month = 4, day = 16) # colocando a hora também conta para o ">="
    fetch_reservas_hoje = """
        SELECT *
        FROM reserva
        WHERE horario >= %s AND (estado = 'Reservado' OR estado = 'Em Espera')
        ORDER BY campo_id_campo, horario, estado DESC
    """

    # executar querys
    cursor.execute(fetch_reservas_hoje, (date,))
    reservas_hoje = cursor.fetchall()
    
    os.system('cls')
    print(" ***** Reserva de campo no Padel Mondego *****\n *")
    #print(" * Campos Disponíveis para hoje,", datetime.now().strftime("%d/%m"))
    print(" * Campos para hoje, 16/04, HORAS (SÓ MOSTRAR A PARTIR DA HORA ATUAL)") # teste
    
    print(" * São as horas que estiverem na atualização! (15h00 = nenhum atualiza)")
    hora_atual = datetime(year = 2024, month = 4, day = 16, hour = 15, minute = 00, second = 00)

    # listar todos os campos e todos os horários
    # estados: reservado; cancelado; finalizado; em espera; em espera cancelado; alterado reservado; alterado finalizado

    # ALTERAR ESTE ARRAY!! ESSA É A SOLUÇÃO!
    horarios_semana = ["15h00", "16h30", "18h00", "19h30", "21h00", "22h30"]
    horarios_fds = ["10h", "11h30", "13h", "14h30", "16h", "17h30", "19h", "20h30"]

    print(" * \n * Campo - 1 * \n * ")
    i = 1
    count_slots_mostrados = 0
    for horario_semana in horarios_semana:
        reservado = False
        # tecnicamente não será necessário este "if" (só apareceram a partir da hora atual)
        #if hora_atual.hour < int(horario_semana[:2]) or (hora_atual.hour == int(horario_semana[:2]) and hora_atual.minute <= int(horario_semana[3:])):
        for reserva_hoje in reservas_hoje:
            if reserva_hoje['campo_id_campo'] == 1 and reserva_hoje['horario'].strftime("%Hh%M") == horario_semana:
                if reserva_hoje['estado'] == 'Reservado':
                    print(" * ", i, " - ", horario_semana, " | Reservado", " | ", reserva_hoje['cliente_utilizador_email'])
                    reservado = True
                    break
        if not reservado:
            print(" * ", i, " - ", horario_semana, " | Livre")
        i += 1
        count_slots_mostrados += 1

    print(" * \n * Campo - 2 * \n * ")
    for horario_semana in horarios_semana:
        reservado = False
        for reserva_hoje in reservas_hoje:
            if reserva_hoje['campo_id_campo'] == 2 and reserva_hoje['horario'].strftime("%Hh%M") == horario_semana:
                if reserva_hoje['estado'] == 'Reservado':
                    print(" * ", i, " - ", horario_semana, " | Reservado", " | ", reserva_hoje['cliente_utilizador_email'])
                    reservado = True
                    break
        if not reservado:
            print(" * ", i, " - ", horario_semana, " | Livre")
        i += 1

    print(" * \n * Campo - 3 * \n * ")
    for horario_semana in horarios_semana:
        reservado = False
        for reserva_hoje in reservas_hoje:
            if reserva_hoje['campo_id_campo'] == 3 and reserva_hoje['horario'].strftime("%Hh%M") == horario_semana:
                if reserva_hoje['estado'] == 'Reservado':
                    print(" * ", i, " - ", horario_semana, " | Reservado", " | ", reserva_hoje['cliente_utilizador_email'])
                    reservado = True
                    break
        if not reservado:
            print(" * ", i, " - ", horario_semana, " | Livre")
        i += 1

    print(" *\n * Outras opções *\n * ")
    print(" * ", i, " - Selecionar outro dia")
    print(" * ", i + 1, " - Regressar")

    # garantir que opção é válida + não reservar um campo que o user tem reservado
    # claro que pode é reservar outros campos que estejam já reservados (ficam Em Espera)
    opcao = 0
    nao_pode_fazer_reserva = False
    regressar = False
    while opcao < 1 or opcao > i + 1 or nao_pode_fazer_reserva:
        opcao = int(input(" *\n * Escolha uma opção -> "))

        campo_escolhido = 0
        # campo 1
        if opcao <= count_slots_mostrados:
            hora_escolhida = horarios_semana[opcao - 1]
            campo_escolhido = 1
        
        # campo 2
        elif opcao > count_slots_mostrados and opcao <= 2 * count_slots_mostrados:
            hora_escolhida = horarios_semana[opcao - 7]
            campo_escolhido = 2

        # campo 3
        elif opcao > 2 * count_slots_mostrados and opcao <= 3 * count_slots_mostrados:
            hora_escolhida = horarios_semana[opcao - 13]
            campo_escolhido = 3
        
        # outro dia
        elif opcao == i:
            efetuar_reserva_outro_dia(connection, utilizador, date)

        # regressar
        elif opcao == i + 1:
            regressar = True
            break
        
        # verificação que não reserva um campo já reservado
        # verificação que não fica em espera para um campo já em espera
        for reserva_hoje in reservas_hoje:
            nao_pode_fazer_reserva = False
            if reserva_hoje['campo_id_campo'] == campo_escolhido and reserva_hoje['horario'].strftime("%Hh%M") == hora_escolhida and reserva_hoje['cliente_utilizador_email'] == utilizador['email'] and reserva_hoje['estado'] == 'Reservado':
                nao_pode_fazer_reserva = True
                print(" * \n * ATENÇÃO -> Não pode reservar um campo que já reservou! * ")
                break
            if reserva_hoje['campo_id_campo'] == campo_escolhido and reserva_hoje['horario'].strftime("%Hh%M") == hora_escolhida and reserva_hoje['cliente_utilizador_email'] != utilizador['email'] and reserva_hoje['estado'] == 'Reservado':
                for res_hoje in reservas_hoje:
                    if res_hoje['horario'].strftime("%Hh%M") == hora_escolhida and res_hoje['cliente_utilizador_email'] == utilizador['email'] and res_hoje['campo_id_campo'] == campo_escolhido and res_hoje['estado'] == 'Em Espera':
                        print(" * \n * ATENÇÃO -> Já está em espera para este campo! * ")
                        nao_pode_fazer_reserva = True
                        break
                if nao_pode_fazer_reserva:
                    break
        
        if opcao < 1 or opcao > i + 1:
            print(" * \n * ATENÇÃO -> Opção inválida! *")

    if not regressar:
    
        # efetuar reserva: "id_reserva, horario, estado, price_id_custo, campo_id_campo, cliente_utilizador_email"
        reserva_a_efetuar = []
        
        # basta modificar o tipo do PK para autoincremento
        fetch_maior_id = """
            SELECT MAX(id_reserva)
            FROM reserva
        """
        cursor.execute(fetch_maior_id)
        ultimo_id = cursor.fetchone()[0]

        # último id
        reserva_a_efetuar.append(ultimo_id + 1)

        # hora escolhida
        hora_escolhida = datetime.strptime(hora_escolhida, "%Hh%M")
        # colocar a data de teste -> 16/04
        hora_escolhida = hora_escolhida.replace(year = 2024, month = 4, day = 16)
        
        reserva_a_efetuar.append(hora_escolhida)
        
        # estado (Reservado ou Em Espera)
        estado = "Reservado"
        for reserva_hoje in reservas_hoje:
            if reserva_hoje['horario'] == hora_escolhida and reserva_hoje['cliente_utilizador_email'] != utilizador['email'] and reserva_hoje['campo_id_campo'] == campo_escolhido:
                estado = "Em Espera"

        reserva_a_efetuar.append(estado)
        
        # custo
        tipo_dia = "Dia de semana"
        tipo_horario = "Normal"
        if hora_escolhida.isoweekday() >= 6:
            tipo_dia = "Fim de semana"
        if hora_escolhida.hour >= 18 and tipo_dia == "Dia de semana":
            tipo_horario = "Nobre"
        
        buscar_lista_preco = """
            SELECT id_custo, preco_atual
            FROM price 
            WHERE ativo = True AND tipo_dia = %s AND horario = %s
        """
        cursor.execute(buscar_lista_preco, (tipo_dia, tipo_horario))
        linha = cursor.fetchone()
        id_custo = linha[0]
        preco_reserva = linha[1]

        reserva_a_efetuar.append(id_custo)

        reserva_a_efetuar.append(campo_escolhido)

        reserva_a_efetuar.append(utilizador['email'])

        if estado == "Em Espera":
            print(" * Ficará em espera para o slot: ", hora_escolhida.strftime("%d/%m"), " | ", hora_escolhida.strftime("%Hh%M"), " | Campo -", campo_escolhido)
        else:
            print(" * A seguinte reserva será efetuada: ", hora_escolhida.strftime("%d/%m"), " | ", hora_escolhida.strftime("%Hh%M"), " | ", preco_reserva, "€ | Campo -", campo_escolhido)

        efetua_reserva = "INSERT INTO reserva VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(efetua_reserva, reserva_a_efetuar)
        connection.commit()

        print(" * \n * Reserva efetuada com sucesso! * ")
        input(" * \n * Regressar - Enter")

# ------------------------------------
def efetuar_reserva_outro_dia(connection, utilizador, date):

    os.system('cls')
    print(" ***** Reserva de campo no Padel Mondego *****\n *")
    print(" * Selecione o dia que quer reservar *\n * ")
    
    # subsituir por dia atual
    # e corrigir o facto de mudar de mês :/
    dia = date.day
    for j in range(dia, dia + 7):
        print(" * ", j , " - ", date.replace(day = j).strftime("%d/%m"))
    
    print(" * \n * ", j + 1, " - Regressar")

    opcao = 0
    while opcao < 1 or opcao > j + 1:
        opcao = int(input(" * Escolha uma opção -> "))

        if opcao == j + 1:
            break
        else:
            dia_escolhido = opcao + dia
            break
    print(" * \n * Dia escolhido -> ", dia_escolhido, "\n * ")
    input(" * \n * Regressar - Enter")
    
# ------------------------------------
def reservas_atuais(connection, utilizador):

    cursor = connection.cursor(cursor_factory = psycopg2.extras.DictCursor)

    # mostra reservas futuras
    fetch_reservas_user = """
        SELECT *
        FROM reserva
        WHERE cliente_utilizador_email = %s
        ORDER BY campo_id_campo, horario
    """

    cursor.execute(fetch_reservas_user, (utilizador['email'],))
    reservas_futuras = cursor.fetchall()

    os.system('cls')
    print(" ***** Reservas Futuras - Padel Mondego *****\n *")
    print(" * Neste menu é possível:")
    print(" * * Consultar as reservas atuais")
    print(" * * Cancelar uma reserva (escolher)")
    print(" * * Consultar reservas em espera\n *")
    
    i = 1
    for reserva_futura in reservas_futuras:
        if reserva_futura['estado'] == "Reservado":
            print(f" * {i}. Campo - {reserva_futura['campo_id_campo']} * ")
            i += 1

        else:
            print(f" * *  Campo - {reserva_futura['campo_id_campo']} * ")
            
        buscar_preco = """
            SELECT preco_atual
            FROM price 
            WHERE id_custo = %s 
        """
        cursor.execute(buscar_preco, (reserva_futura['price_id_custo'],))
        preco = cursor.fetchone()[0]

        print(" *   ", reserva_futura['horario'].strftime("%d/%m"), ", ", reserva_futura['horario'].strftime("%Hh%M"), " | ", preco, "€ | ", reserva_futura['estado'], "\n *")

    print(f" * {i}. Regressar")

    opcao = 0
    while opcao < 1 or opcao > i + 1:
        opcao = int(input(" * \n * Escolha uma opção -> "))

        if opcao == i:
            break
        
        id_reserva_cancelar = reservas_futuras[opcao - 1]['id_reserva']

        # estado fica "Cancelado"
        cancelar_reserva = """
            UPDATE reserva
            SET estado = 'Cancelado'
            WHERE id_reserva = %s
        """
        cursor.execute(cancelar_reserva, (id_reserva_cancelar,))
        connection.commit()

        print(" * Reserva cancelada com sucesso!")

        input(" * \n * Regressar - Enter")

# ------------------------------------
def historico_reservas(connection, utilizador):
    
    cursor = connection.cursor(cursor_factory = psycopg2.extras.DictCursor)

    # hora atual teste -> 18h00
    horario_atual = datetime(year = 2024, month = 4, day = 16, hour = 18, minute = 00, second = 00)

    fetch_historico_reservas = """
        SELECT horario, estado, price_id_custo, campo_id_campo, cliente_utilizador_email
        FROM reserva
        WHERE cliente_utilizador_email = %s AND horario < %s
        ORDER BY horario, campo_id_campo
    """
    cursor.execute(fetch_historico_reservas, [(utilizador['email'],), horario_atual])
    linhas = cursor.fetchall()

    os.system('cls')
    print(" ***** Hisórico de Reservas - Padel Mondego *****\n *")

    for linha in linhas:
        print(" *  Campo", linha['campo_id_campo'], "- ", linha['horario'].strftime("%d/%m"), " * ")

        buscar_preco = """
            SELECT preco_atual
            FROM price 
            WHERE id_custo = %s 
        """
        cursor.execute(buscar_preco, (linha['price_id_custo'],))
        preco = cursor.fetchone()[0]

        print(" * ", linha['horario'].strftime("%Hh%M"), " | ", preco, "€", " | ", linha['estado'], "\n *")

    input(" * \n * Regressar - Enter")

# ------------------------------------
# retorna "super_admin", "admin" ou "cliente"
def tipo_utilizador(connection, utilizador):

    tipo_user = None

    cursor = connection.cursor(cursor_factory = psycopg2.extras.DictCursor)

    fetch_admins = """
        SELECT *
        FROM utilizador as u, administrador as a
        WHERE u.email = a.utilizador_email AND u.email = %s
    """

    # executar querys
    cursor.execute(fetch_admins, (utilizador['email'],))
    linha = cursor.fetchone()

    if linha is not None:
        if linha['super_admin']:
            tipo_user = 'super_admin'
        else:
            tipo_user = 'admin'
    else:
        tipo_user = 'cliente'

    return tipo_user

def login(connection):

    os.system('cls')

    print(" ***** Login *****")
    print(" * \n * Login com os seus dados\n *")

    email_invalido = True
    passe_invalida = True

    while email_invalido or passe_invalida:

        email = str(123)
        while email.isdigit():
            email = input(" * Email: ")
            if email.isdigit():
                print("\n *** ATENÇÃO -> Input inválido ***")

        passe = str(123)
        while passe.isdigit():
            passe = input(" * Password: ")
            if passe.isdigit():
                print("\n *** ATENÇÃO -> Input inválido! ***")

        # fetch de utilizadores
        cursor = connection.cursor(cursor_factory = psycopg2.extras.DictCursor)
        fetch_utilizadores = " SELECT email, passe, nome FROM utilizador WHERE email = %s"
        cursor.execute(fetch_utilizadores, (email,))
        linha = cursor.fetchone()

        # verificar se o utilizador existe
        utilizador = []
        if linha is None:
            email_invalido = True
            passe_invalida = True

        elif email == linha['email']:
            email_invalido = False

            if passe == linha['passe']:
                passe_invalida = False
                nome = linha['nome']
                utilizador = {'email': email, 'passe': passe, 'nome': nome}
            else:
                passe_invalida = True

        if email_invalido or passe_invalida:
            print(" * \n *** ATENÇÃO -> Um dos campos está inválido! ***")

    print(" * \n * \n * Login efetuado com sucesso! * ")

    # verifica se é admin ou cliente
    tipo_user = tipo_utilizador(connection, utilizador)

    if tipo_user == 'admin':
        utilizador['super_admin'] = False
        tipo_user = "Admin"
    elif tipo_user == 'super_admin':
        utilizador['super_admin'] = True
        tipo_user = "Super Admin"
    elif tipo_user == 'cliente':
        fetch_utilizadores = " SELECT nif, numero_telefone FROM cliente WHERE utilizador_email = %s"
        cursor.execute(fetch_utilizadores, (email,))
        nif, numero_telefone = cursor.fetchone()
        utilizador.update({'nif': nif, 'numero_telefone': numero_telefone})
        tipo_user = "Cliente"
    else:
        print("Erro na função de login!")
        raise Exception("Erro na função de login!")

    print(" * \n * Bem vindo,", tipo_user, nome)
    time.sleep(1)
    return utilizador

def register(connection):
    os.system('cls')

    user = []

    print(" ***** Registar *****")
    print(" * \n * Registe os seus dados\n *")

    # adicionar whiles de segurança
    nome = input(" * Nome: ")

    email_existe = True
    while email_existe:
        email = input(" * Email: ")

        # verificar se o email/nome já existe
        cursor = connection.cursor(cursor_factory = psycopg2.extras.DictCursor)

        fetch_utilizadores = """
            SELECT nome, email, passe
            FROM utilizador
        """

        cursor.execute(fetch_utilizadores)
        linhas = cursor.fetchall()

        for linha in linhas:
            if email == linha['email']:
                email_existe = True
                print(" * \n *** ATENÇÃO -> Email já registado! ***")
                break
            else:
                email_existe = False

    password = input(" * Password: ")

    # tem de ser por esta ordem!
    user.append(email)
    user.append(password)
    user.append(nome)

    # insere utilizador (antes de inserir admin ou cliente)
    cursor = connection.cursor()
    insere_user = "INSERT INTO utilizador VALUES (%s, %s, %s)"
    cursor.execute(insere_user, user)
    connection.commit()

    print(" * \n * \n * Tipo de utilizador\n *")
    print(" * 1 - Admin")
    print(" * 2 - Cliente\n * ")

    tipo = int(input(" * Escolha uma opção -> "))

    if tipo == 1:

        user_admin = []

        # fetch último admin_id
        cursor = connection.cursor(cursor_factory = psycopg2.extras.DictCursor)

        fetch_restantes_admins = """
            SELECT a.admin_id
            FROM administrador as a
            ORDER BY a.admin_id DESC
        """

        cursor.execute(fetch_restantes_admins)
        linha = cursor.fetchone()
        ultimo_admin_id, = linha

        # atribuir características de admin
        user_admin.append(ultimo_admin_id + 1)
        print(" * \n * ")
        print(" * Super Admin\n * ")
        print(" * 1 - Sim")
        print(" * 0 - Não\n * ")
        sa = int(input(" * Escolha uma opção -> "))

        if sa:
            user_admin.append(True)
        else:
            user_admin.append(False)

        user_admin.append(email)

        # inserir utilizador + admin
        cursor = connection.cursor()

        print(" * \n * \n * Registo efetuado com os dados acima indicados! * ")

        insere_admin = "INSERT INTO administrador VALUES (%s, %s, %s)"

        cursor.execute(insere_admin, user_admin)
        connection.commit()

        user.append(user_admin)

    else:
        user_cliente = []

        print(" * \n * ")
        nif = str(9999999999)
        while len(nif) > 9 or not nif.isdigit():
            nif = input(" * NIF: ")
            if len(nif) > 9 or not nif.isdigit():
                print("\n *** ATENÇÃO -> NIF inválido! ***")

        telemovel = str(9999999999)
        while len(telemovel) > 9 or not telemovel.isdigit():
            telemovel = input(" * Telemóvel: ")
            if len(telemovel) > 9 or not telemovel.isdigit():
                print("\n *** ATENÇÃO -> Telemóvel inválido! ***")

        user_cliente.append(nif)
        user_cliente.append(telemovel)
        user_cliente.append(email)

        # inserir utilizador + cliente
        cursor = connection.cursor()

        print(" * \n * \n * Registo efetuado com os dados acima indicados! * ")

        insere_admin = "INSERT INTO cliente VALUES (%s, %s, %s)"

        cursor.execute(insere_admin, user_cliente)
        connection.commit()

        user.append(user_cliente)

    time.sleep(2)
    os.system('cls')
    return user

# ------------------------------------
def sair():
    print("a sair do programa...")
    return None

# ------------------------------------
def apresentar_menu_admin(tipo_user):
    os.system('cls')
    print(" ***** Menu Admin *****\n *")
    print(" * 1 - Alterar Reservas")
    print(" * 2 - Alterar Preços")
    print(" * 3 - Estatísticas")
    print(" * 4 - Mensagem Geral")
    print(" * 5 - Mensagem Privada")
    
    if tipo_user == 'admin':
        print(" * 6 - Logout | Sair\n *")
    else:
        print(" * 6 - Gestão de Admins")
        print(" * 7 - Logout | Sair\n *")

    opcao = 0
    while opcao < 1 or (opcao > 6 and tipo_user == 'admin') or (opcao > 7 and tipo_user == 'super_admin'):
        opcao = int(input(" * Escolha uma opção -> "))

    return opcao

# ------------------------------------
def apresentar_menu_cliente():
    os.system('cls')
    print(" ***** Menu Cliente *****\n *")
    print(" * 1 - Informações e Perfil")
    print(" * 2 - Reservar Campo")
    print(" * 3 - Reservas atuais")
    print(" * 4 - Histórico de Reservas")
    print(" * 5 - Logout | Sair\n *")

    opcao = 0
    while opcao < 1 or opcao > 5:
        opcao = int(input(" * Escolha uma opção -> "))

    return opcao

# ------------------------------------
def menu():

    print(" ***** Padel Mondego *****\n")
    print(" * Bem Vindo à mais recente aplicação de reservas de campos de Padel")
    print(" * ")
    print(" * 1 - Login")
    print(" * 2 - Registar")
    print(" * 3 - Sair\n * ")

    opcao = 0
    while opcao < 1 or opcao > 3:
        opcao = int(input(" * Escolha uma opção -> "))

    return opcao

# ------------------------------------
def atualiza_campos(connection):

    cursor = connection.cursor(cursor_factory = psycopg2.extras.DictCursor)

    # recebe hora atual
    # current_datetime = datetime.now()

    current_datetime = datetime(year = 2024, month = 4, day = 16, hour = 14, minute = 00, second = 00)
    diferenca = current_datetime - timedelta(hours = 1, minutes = 30)

    # dar update das reservas em que já passou 1h30
    # imaginemos -> jogo das 15h e são 16h50
    # 16h50 - 1h30 = 15h20; logo, horario (15h) < 15h20 
    update_jogos_a_decorrer = """
        UPDATE reserva
        SET estado = 'Finalizado'
        WHERE estado = 'Reservado' AND horario < %s
    """

    cursor.execute(update_jogos_a_decorrer, (diferenca,))
    connection.commit()

    if cursor.rowcount > 0:
        print("Fields updated successfully\n\n")
    else:
        print("\n")

# ------------------------------------
def database_connection():
    print("Conexão com base de dados")

    try:
        connection = psycopg2.connect(
            user = "postgres",
            password = "pepas1206",
            host = "127.0.0.1",
            port = "5432",
            database = "padel mondego"
        )

        cursor = connection.cursor()
        cursor.execute("SELECT version();")
        record = cursor.fetchone()
        print("You are connected to - ", record)
        return connection

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
        return None

# ------------------------------------
if __name__ == '__main__':
    main()