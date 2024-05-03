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
    registar = False
    opcao = 1
    while opcao > 0 or opcao < 3:
        opcao = menu()
        if opcao == 1:

            # encriptar passwords :)
            utilizador = login(connection)
            registar = False

            # definir o tipo de utilizador
            tipo_user = tipo_utilizador(connection, utilizador)

        elif opcao == 2:
            utilizador = register(connection)
            registar = True

        elif opcao == 3:
            print(" * Até uma próxima! *")
            registar = True
            break

        if not registar:
            if tipo_user == "Ambos":
                
                os.system('cls')
                print(" * Pretende aceder como cliente ou administrador?\n *")
                print(" * 1. Cliente")
                print(" * 2. Administrador")

                opcao_menu = 0
                while opcao_menu < 1 or opcao_menu > 2:
                    opcao_menu = int(input(" * \n * Escolha uma opção -> "))

                    if opcao_menu == 1:
                        tipo_user = "Cliente"
                    elif opcao_menu == 2:
                        tipo_user = "Admin"

            if tipo_user == 'Admin' or tipo_user == 'Super Admin':
                menu_admin(connection, utilizador, tipo_user)
            else:
                menu_cliente(connection, utilizador)

    print("fim")

# ------------------------------------
def menu_admin(connection, utilizador, tipo_user):
    
    opcao = 1 
    while opcao > 0 or opcao < 7:
        opcao = apresentar_menu_admin(tipo_user, utilizador)

        if opcao == 1:
            alterar_reservas_menu(connection)
        
        elif opcao == 2:
            alterar_precos(connection)

        elif opcao == 3:
            estatisticas(connection)
            
        elif opcao == 4:
            print("mensagem geral")
        
        elif opcao == 5:
            print("mensagem privada")

        elif opcao == 6 and tipo_user == 'Admin':
            os.system('cls')
            return None

        elif opcao == 6 and tipo_user == 'Super Admin':
            gestao_admins(connection)
            
        elif opcao == 7 and tipo_user == 'Super Admin':
            os.system('cls')
            return None

# ------------------------------------
def gestao_admins(connection):

    opcao = 0
    regressar = False
    while opcao < 1 or opcao > 4:

        os.system('cls')
        print(" ***** Gestão de Administradores ***** \n *")
        print(" * 1. Adicionar Administrador")
        print(" * 2. Remover Administrador")
        print(" * 3. Regressar")
        opcao = int(input(" * \n * Escolha uma opção -> "))

        if opcao == 3:
            regressar = True
            break

        if not regressar:
            
            if opcao == 1:
                voltar = adicionar_admin(connection)
                if voltar:
                    opcao = 0
            
            elif opcao == 2:
                voltar = remover_admin(connection)
                if voltar:
                    opcao = 0
            
            elif opcao == 3:
                opcao = 0

# ------------------------------------
def adicionar_admin(connection):

    cursor = connection.cursor(cursor_factory = psycopg2.extras.DictCursor)
    fetch_clientes = """
        SELECT *
        FROM cliente AS c, utilizador AS u
        WHERE c.utilizador_email = u.email
    """ 
    cursor.execute(fetch_clientes)
    clientes = cursor.fetchall()

    fetch_admins = """
        SELECT *
        FROM administrador AS a, utilizador AS u
        WHERE a.utilizador_email = u.email
    """
    cursor.execute(fetch_admins)
    admins = cursor.fetchall()

    table = PrettyTable()
    table_admins = PrettyTable()
    table.field_names = ["#", "Nome", "Email"]
    table_admins.field_names = ["#", "Nome", "Email"]
    for j , admin in enumerate(admins, start = 1):
        table_admins.add_row([j, admin['nome'], admin['email']])

    i = 1
    cliente_valido = []
    for cliente in clientes:
        if cliente['email'] not in [admin['email'] for admin in admins]:
            table.add_row([i, cliente['nome'], cliente['email']])
            cliente_valido.append(cliente)
            i += 1
        else:
            table.add_row([" ", cliente['nome'], cliente['email']])

    os.system('cls')
    print(" ***** Adicionar Administrador *****\n ")
    print(" * Administradores *\n")
    print(table_admins)
    print(" \n* Clientes *\n")
    print(table)
    print(" \n * ", i , ". Regressar\n *")

    opcao = 0
    regressar = False
    while opcao < 1 or opcao > i:
        opcao = int(input(" * Escolha um cliente -> "))

        if opcao == i:
            regressar = True
            break
        
        elif opcao < i:
            cliente = cliente_valido[opcao - 1]
            break
    
    if not regressar:

        adicionar_admin = """
            INSERT INTO administrador (super_admin, utilizador_email)
            VALUES (%s, %s)
        """
        cursor.execute(adicionar_admin, (False, cliente['email'],))
        connection.commit()

        print(" * Administrador adicionado com sucesso!")
        input(" * \n * Regressar - Enter")
        
    return regressar

# ------------------------------------
def remover_admin(connection):

    cursor = connection.cursor(cursor_factory = psycopg2.extras.DictCursor)
    fetch_clientes = """
        SELECT *
        FROM administrador, utilizador
        WHERE super_admin = False AND utilizador_email = email
    """ 
    cursor.execute(fetch_clientes)
    admins = cursor.fetchall()

    table = PrettyTable()
    table.field_names = ["#", "Nome", "Email"]
    for i, cliente in enumerate(admins, start = 1):
        table.add_row([i, cliente['nome'], cliente['email']])

    os.system('cls')
    print(" ***** Remover Administrador *****\n ")
    print(table)
    print(" \n * ", len(admins) + 1, ". Regressar\n *")

    opcao = 0
    regressar = False
    while opcao < 1 or opcao > len(admins) + 1:
        opcao = int(input(" * Escolha um cliente -> "))

        if opcao == len(admins) + 1:
            regressar = True
            break
        
        elif opcao < len(admins) + 1:
            admin = admins[opcao - 1]
            break
    
    if not regressar:

        remover_admin = """
            DELETE FROM administrador
            WHERE utilizador_email = %s;
        """
        cursor.execute(remover_admin, (admin['email'],))
        connection.commit()

        print(" *\n * Administrador removido com sucesso!")
        input(" * \n * Regressar - Enter")
        
    return regressar

# ------------------------------------
def estatisticas(connection):
    
    cursor = connection.cursor(cursor_factory = psycopg2.extras.DictCursor)
    
    os.system('cls')
    print(" ***** Estatísticas *****\n *")
    print(" * * Num determinado período,\n * ")
    print(" * 1. Campo mais reservado")
    print(" * 2. Horário mais reservado")
    print(" * 3. Listar campos, por horário, sem reservas")
    print(" * 4. Listar reservas canceladas")
    print(" * 5. Listar reservas alteradas")
    print(" * 6. Listar períodos em que os clientes pediram para receber notificação")
    print(" * 7. Regressar")

    opcao = 0
    regressar = False
    while opcao < 1 or opcao > 7:
        opcao = int(input(" * \n * Escolha uma opção -> "))

        if opcao == 7:
            regressar = True
            break

    if not regressar:

        if opcao == 1:
            tipo_menu = " ***** Campo mais reservado *****\n *"
            data_inicial, data_final = menu_periodo(tipo_menu)

            fetch_reservas_periodo = """
                SELECT *
                FROM reserva
                WHERE horario >= %s AND horario <= %s
            """
            cursor.execute(fetch_reservas_periodo, (data_inicial, data_final))
            mais_reservas_periodo = cursor.fetchall()

            count_campos = {1: 0, 2: 0, 3: 0}
            for reserva in mais_reservas_periodo:
                count_campos[reserva['campo_id_campo']] += 1

            os.system('cls')
            print(" ***** Campos mais reservado *****\n *")
            print(" * Período: (", data_inicial, " a ", data_final, ")\n ")
            sorted_count = sorted(count_campos.items(), key = lambda x: x[1], reverse = True)

            table = PrettyTable()
            table.field_names = ["Campo", "# Reservas"]
            for campo, reservations in sorted_count:
                if reservations > 0:
                    table.add_row([campo, reservations])

            print(table)
            input(" \n * Regressar - Enter")
        
        elif opcao == 2:
            tipo_menu = " ***** Horário mais reservado *****\n *"
            data_inicial, data_final = menu_periodo(tipo_menu)

            fetch_horarios_periodo = """
                SELECT *
                FROM reserva
                WHERE horario >= %s AND horario <= %s
            """
            cursor.execute(fetch_horarios_periodo, (data_inicial, data_final))
            mais_horario_periodo = cursor.fetchall()

            count_horarios = {"15h00": 0, "16h30": 0, "18h00": 0, "19h30": 0, "21h00": 0, "22h30": 0}
            for reserva in mais_horario_periodo:
                # ATENÇÃO!! QUANDO SE CORRIGIR PARA FIM DE SEMANA TIRAR ISTO
                if reserva['horario'].strftime("%Hh%M") not in count_horarios:
                    continue
                count_horarios[reserva['horario'].strftime("%Hh%M")] += 1

            os.system('cls')
            print(" ***** Horário mais reservado *****\n *")
            print(" * Período: (", data_inicial, " a ", data_final, ")\n ")
            sorted_count = sorted(count_horarios.items(), key = lambda x: x[1], reverse = True)

            table = PrettyTable()
            table.field_names = ["Horário", "# Reservas"]
            for horario, reservations in sorted_count:
                if reservations > 0:
                    table.add_row([horario, reservations])

            print(table)
            input(" \n * Regressar - Enter")
        
        elif opcao == 3:
            tipo_menu = " ***** Campos sem reservas *****\n *"
            data_inicial, data_final = menu_periodo(tipo_menu)

            fetch_horarios_periodo = """
                SELECT *
                FROM reserva
                WHERE horario >= %s AND horario <= %s
                ORDER BY campo_id_campo, horario
            """
            cursor.execute(fetch_horarios_periodo, (data_inicial, data_final))
            reservas = cursor.fetchall()

            numero_dias = (data_final - data_inicial).days

            count_campos = {1: 0, 2: 0, 3: 0}
            count_horarios = {"15h00": 0, "16h30": 0, "18h00": 0, "19h30": 0, "21h00": 0, "22h30": 0}
            for reserva in reservas:
                if reserva['estado'] == 'Reservado' or reserva['estado'] == 'Em Espera' and reserva['horario'].strftime("%Hh%M") in count_horarios:
                    count_campos[reserva['campo_id_campo']] += 1

            # falta verificar fins de semana...!
            count_campos[1] = len(count_horarios) * numero_dias - count_campos[1]
            count_campos[2] = len(count_horarios) * numero_dias - count_campos[2]
            count_campos[3] = len(count_horarios) * numero_dias - count_campos[3]

            os.system('cls')
            print(" ***** Campos sem reservas *****\n *")
            print(" * Período: (", data_inicial, " a ", data_final, ")\n ")
            sorted_count = sorted(count_campos.items(), key = lambda x: x[1], reverse = True)

            for campo, reservations in sorted_count:
                print(f" * Campo {campo} não teve {reservations} reservas\n *")
            
            input(" \n * Regressar - Enter")
        
        elif opcao == 4:
            tipo_menu = " ***** Reservas canceladas *****\n *"
            data_inicial, data_final = menu_periodo(tipo_menu)

            fetch_reservas_canceladas = """
                SELECT *
                FROM reserva
                WHERE horario >= %s AND horario <= %s AND estado = 'Cancelado'
                ORDER BY horario
            """
            cursor.execute(fetch_reservas_canceladas, (data_inicial, data_final))
            reservas_canceladas = cursor.fetchall()

            os.system('cls')
            print(" ***** Reservas canceladas *****\n *")
            print(" * Período: (", data_inicial, " a ", data_final, ")\n ")

            table = PrettyTable()
            table.field_names = ["Email Cliente", "Horário", "Campo"]
            for reserva in reservas_canceladas:
                table.add_row([reserva['cliente_utilizador_email'], reserva['horario'].strftime("%d/%m, %Hh%M"), reserva['campo_id_campo']])

            print(table)
            input(" \n * Regressar - Enter")
        
        elif opcao == 5:
            tipo_menu = " ***** Reservas alteradas *****\n *"
            data_inicial, data_final = menu_periodo(tipo_menu)

            fetch_reservas_canceladas = """
                SELECT *
                FROM reserva
                WHERE horario >= %s AND horario <= %s AND estado = 'Alterado Reservado' or estado = 'Alterado Finalizado'
                ORDER BY horario
            """
            cursor.execute(fetch_reservas_canceladas, (data_inicial, data_final))
            reservas_canceladas = cursor.fetchall()

            os.system('cls')
            print(" ***** Reservas canceladas *****\n *")
            print(" * Período: (", data_inicial, " a ", data_final, ")\n ")

            table = PrettyTable()
            table.field_names = ["Email Cliente", "Horário", "Campo", "Estado"]
            for reserva in reservas_canceladas:
                table.add_row([reserva['cliente_utilizador_email'], reserva['horario'].strftime("%d/%m, %Hh%M"), reserva['campo_id_campo'], reserva['estado']])

            print(table)
            input(" \n * Regressar - Enter")
        
        elif opcao == 6:
            print("Receber notificação")
            input(" \n * Regressar - Enter")

# ------------------------------------
def menu_periodo(tipo_menu):
    nao_preenchido_inicial = True
    nao_preenchido_final = True
    data_inicial = date(year = 2000, month = 1, day = 1)
    data_final = date(year = 2000, month = 1, day = 1)
    while nao_preenchido_inicial or nao_preenchido_final:
        os.system('cls')
        print(tipo_menu)
        print(" * Período: (", data_inicial, " - ", data_final, ")\n *")

        if nao_preenchido_inicial:
            while True:
                data_inicial_str = input(" * Data inicial (yyyy-mm-dd): ")
                if data_inicial_str != "aaaa-mm-dd":
                    try:
                        data_inicial = date.fromisoformat(data_inicial_str)
                        nao_preenchido_inicial = False
                        break
                    except ValueError:
                        print(" * Data inválida. Insira no formato yyyy-mm-dd.")
        
        elif nao_preenchido_final:
            while True:
                data_final_str = input(" * Data final (yyyy-mm-dd): ")
                if data_final_str != "aaaa-mm-dd":
                    try:
                        data_final = date.fromisoformat(data_final_str)
                        nao_preenchido_final = False
                        break
                    except ValueError:
                        print(" * \n * Data inválida. Insira no formato yyyy-mm-dd.")
    
    data_final = data_final + timedelta(days = 1)
    return data_inicial, data_final

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
    print(" * * Cancelar reservas")
    print(" * * * Reservas 'Em Espera' apenas podem ser canceladas\n")

    table = PrettyTable()
    table.field_names = ["#", "Cliente", "Email", "Horário", "Campo", "Estado"]

    i = 1
    current_user = reservas_futuras[0]['email']
    numero_reservas_futuras = len(reservas_futuras)
    
    # lista de reservas, sem as canceladas
    reservas_futuras_corretas = []
    
    for reserva_futura in reservas_futuras:
        if i + 1 < numero_reservas_futuras:
            next_user = reservas_futuras[i]['email']
            if next_user != current_user:
                if reserva_futura['estado'] == 'Cancelado' or reserva_futura['estado'] == 'Em Espera Cancelado':
                    table.add_row([" ", reserva_futura['nome'], reserva_futura['email'],
                        reserva_futura['r_horario'].strftime("%d/%m, %Hh%M"), reserva_futura['campo_id_campo'],
                        reserva_futura['estado']], divider = True)
                else:
                    table.add_row([i, reserva_futura['nome'], reserva_futura['email'],
                        reserva_futura['r_horario'].strftime("%d/%m, %Hh%M"), reserva_futura['campo_id_campo'],
                        reserva_futura['estado']], divider = True)
                    reservas_futuras_corretas.append(reserva_futura)
                    i += 1
            else:
                if reserva_futura['estado'] == 'Cancelado' or reserva_futura['estado'] == 'Em Espera Cancelado':
                    table.add_row([" ", reserva_futura['nome'], reserva_futura['email'],
                        reserva_futura['r_horario'].strftime("%d/%m, %Hh%M"), reserva_futura['campo_id_campo'],
                        reserva_futura['estado']])
                else:
                    table.add_row([i, reserva_futura['nome'], reserva_futura['email'],
                        reserva_futura['r_horario'].strftime("%d/%m, %Hh%M"), reserva_futura['campo_id_campo'],
                        reserva_futura['estado']])
                    reservas_futuras_corretas.append(reserva_futura)
                    i += 1
            current_user = next_user                
        else:
            if reserva_futura['estado'] == 'Cancelado' or reserva_futura['estado'] == 'Em Espera Cancelado':
                table.add_row([" ", reserva_futura['nome'], reserva_futura['email'],
                    reserva_futura['r_horario'].strftime("%d/%m, %Hh%M"), reserva_futura['campo_id_campo'],
                    reserva_futura['estado']])
            else:
                table.add_row([i, reserva_futura['nome'], reserva_futura['email'],
                        reserva_futura['r_horario'].strftime("%d/%m, %Hh%M"), reserva_futura['campo_id_campo'],
                        reserva_futura['estado']])
                reservas_futuras_corretas.append(reserva_futura)
                i += 1

    print(table)

    print(f"\n * {i}. Regressar")

    opcao = 0
    regressar = False
    while opcao < 1 or opcao > i:
        opcao = int(input(" * \n * Escolha uma reserva -> "))

        if opcao == i:
            regressar = True
            break

        elif opcao < i:

            reserva_a_alterar = reservas_futuras_corretas[opcao - 1]

            opcao_admin = 0
            if reserva_a_alterar['estado'] == 'Em Espera':
                print(" *\n * Apenas pode cancelar esta reserva\n *")
                input(" * \n * Proceder - Enter")
                opcao_admin = 2
            
            else:
                print(" * \n * 1 - Alterar Reserva")
                print(" * 2 - Cancelar Reserva")
                print(" * 3 - Regressar\n * ")

                while opcao_admin < 1 or opcao_admin > 3:
                    opcao_admin = int(input(" * Escolha uma opção -> "))
                    
                    if opcao_admin == 3:
                        regressar = True
                        break

    if not regressar:
        
        # alterar reserva
        if opcao_admin == 1:
            alterar_reservas(connection, reserva_a_alterar, reservas_futuras_corretas)

        elif opcao_admin == 2:
            
            ja_cancelado = False
            if reserva_a_alterar['estado'] == 'Cancelado':
                print(" * \n * ATENÇÃO -> Reserva já cancelada! * ")
                input(" * Regressar - Enter")
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
def alterar_reservas(connection, reserva_a_alterar, reservas_futuras_corretas):
    
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

    opcao_alterar = 0
    while opcao_alterar < 1 or opcao_alterar > 3:
        opcao_alterar = int(input(" * \n * Escolha uma opção -> "))

    # alterar campo
    if opcao_alterar == 1:
        novo_campo = reserva_a_alterar['campo_id_campo']

        outros_campos = []
        table_3 = PrettyTable()
        table_3.field_names = ["Cliente", "Email", "Horário", "Situação", "Preço", "Campo", "Estado"]
        for reserva_futura in reservas_futuras_corretas:
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
            SET campo_id_campo = %s,
                estado = 'Alterado Reservado'
            WHERE WHERE id_reserva = %s
        """
        cursor.execute(atualizar_reserva, (novo_campo, reserva_a_alterar['id_reserva']))
        connection.commit()

        print(" * Campo atualizado!")
        input(" * \n * Regressar - Enter")

    # alterar dia
    elif opcao_alterar == 2:

        # dia da reserva a alterar
        dia = reserva_a_alterar['r_horario'].day
        
        # dia de hoje
        hoje = datetime(year = 2024, month = 4, day = 16).day
        #hoje = datetime.now().day

        # ALTERAR FILTRAR AQUI!!!
        
        outros_dias = []
        table_4 = PrettyTable()
        table_4.field_names = ["Cliente", "Email", "Horário", "Situação", "Preço", "Campo", "Estado"]
        for reserva_futura in reservas_futuras_corretas:
            if reserva_futura['campo_id_campo'] == reserva_a_alterar['campo_id_campo'] and reserva_futura['r_horario'].strftime("%Hh%M") == reserva_a_alterar['r_horario'].strftime("%Hh%M") and reserva_futura['r_horario'].day != dia:
                outros_dias.append(reserva_futura['r_horario'].day)
                apresentar_situacao = f"{reserva_futura['tipo_dia']}, {reserva_futura['p_horario']}"
                apresentar_preco = f"{reserva_futura['preco_atual']} €"
                table_4.add_row([reserva_futura['nome'], reserva_futura['email'],
                            reserva_futura['r_horario'].strftime("%d/%m, %Hh%M"), apresentar_situacao,
                            apresentar_preco, reserva_futura['campo_id_campo'], reserva_futura['estado']], divider = True)

        if len(outros_dias) > 0:
            print(" *\n * Outras reservas, na mesma hora/campo:\n ")
            print(table_4)
        
        else:
            print(" * \n * Não há reservas noutros campos, nas mesmas situações* ")

        novo_dia = dia
        opcao_invalida_2 = True
        while novo_dia < hoje or novo_dia > (hoje + 7) or novo_dia == dia or opcao_invalida_2:
            
            novo_dia = int(input(f"\n * Indique o novo dia, entre {hoje} e {hoje + 7} -> "))
            
            if novo_dia == reserva_a_alterar['r_horario'].day:
                print(" * \n * ATENÇÃO -> Dia igual ao anterior! * ")
            
            elif novo_dia > hoje + 7 or novo_dia < hoje:
                print(" * \n * ATENÇÃO -> Apenas pode mudar até 7 dias! *")
            
            elif novo_dia in outros_dias:
                print(" * \n * ATENÇÃO -> Campo já reservado! * ")
            
            else:
                opcao_invalida_2 = False
                
        novo_horario = reserva_a_alterar['r_horario'].replace(day = novo_dia)
        # atualizar a reserva selecionada
        atualizar_reserva_dia = """
            UPDATE reserva
            SET horario = %s,
                estado = 'Alterado Reservado'
            WHERE id_reserva = %s
        """
        cursor.execute(atualizar_reserva_dia, (novo_horario, reserva_a_alterar['id_reserva']))
        connection.commit()

        print(" * Dia atualizado!")
        input(" * \n * Regressar - Enter")

    # alterar hora
    elif opcao_alterar == 3:
        nova_hora = reserva_a_alterar['r_horario'].strftime("%Hh%M")

        horarios_semana = ["15h00", "16h30", "18h00", "19h30", "21h00", "22h30"]
        horarios_fds = ["10h00", "11h30", "13h00", "14h30", "16h00", "17h30", "19h00", "20h30"]

        horario = []
        if reserva_a_alterar['r_horario'].isoweekday() >= 6:
            horario = horarios_fds
        else:
            horario = horarios_semana

        table_5 = PrettyTable()
        table_5.field_names = ["#", "Horário", "Estado", "Cliente"]

        i = 1
        escolher_horario = []
        for horario_semana in horario:
            reservado = False
            for reserva_hoje in reservas_futuras_corretas:
                if reserva_hoje['campo_id_campo'] == reserva_a_alterar['campo_id_campo'] and reserva_hoje['r_horario'].strftime("%Hh%M") == horario_semana and reserva_hoje['r_horario'].day == reserva_a_alterar['r_horario'].day:
                    table_5.add_row([" ", horario_semana, reserva_hoje['estado'], reserva_hoje['email']])
                    reservado = True
                    break
            if not reservado:
                table_5.add_row([i, horario_semana, "Livre", " "])
                escolher_horario.append(horario_semana)
                i += 1

        print(" *\n * Horários disponíveis, no mesmo campo/dia *\n ")
        print(table_5, "\n")

        opcao_invalida_3 = True
        while opcao_invalida_3:
            opcao_hora = int(input(" * Indique a nova hora: "))

            nova_hora = escolher_horario[opcao_hora - 1]

            if nova_hora not in horario:
                print(" * \n * ATENÇÃO -> Hora inválida! * ")
            
            elif nova_hora == reserva_a_alterar['r_horario'].strftime("%Hh%M"):
                print(" * \n * ATENÇÃO -> Hora igual ao anterior! * ")
            
            else:
                opcao_invalida_3 = False

        novo_horario = reserva_a_alterar['r_horario'].replace(hour = int(nova_hora[:2]), minute = int(nova_hora[3:5]))
        # atualizar a reserva selecionada
        atualizar_reserva_hora = """
            UPDATE reserva
            SET horario = %s,
                estado = 'Alterado Reservado'
            WHERE id_reserva = %s
        """
        cursor.execute(atualizar_reserva_hora, (novo_horario, reserva_a_alterar['id_reserva']))
        connection.commit()

        print(" * Hora atualizada!")
        input(" * \n * Regressar - Enter")


# ------------------------------------
def menu_cliente(connection, utilizador):

    opcao = 1
    while opcao > 0 or opcao < 5:
        opcao = apresentar_menu_cliente(utilizador)

        if opcao == 1:
            voltar = informacoes_e_perfil(connection, utilizador)
            if voltar:
                opcao = 0

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
def informacoes_e_perfil(connection, utilizador):
    
    cursor = connection.cursor(cursor_factory = psycopg2.extras.DictCursor)
    fetch_campos = """
        SELECT *
        FROM campo
    """
    cursor.execute(fetch_campos)
    campos = cursor.fetchall()

    fetch_cliente = """
        SELECT *
        FROM cliente AS c, utilizador
        WHERE c.utilizador_email = %s AND c.utilizador_email = email
    """
    cursor.execute(fetch_cliente, (utilizador['email'],))
    cliente = cursor.fetchone()

    os.system('cls')
    print(" ***** Informações do clube Padel Mondego *****\n *")
    print(" * Lorem ipsum dolor sit amet, consectetur adipiscing elit.\n * Nunc cursus porttitor nisi a venenatis. \n * Mauris elementum tincidunt nisi eu consequat.\n * Cras tristique libero cursus sem eleifend facilisis.\n * In hac habitasse platea dictumst.")

    print(" \n***** Descrição de Campos *****\n *")
    for campo in campos:
        print(" *", campo['descricao'])

    print("\n ***** Informações do Cliente *****\n")
    table = PrettyTable()
    table.field_names = ["#", "Info", "Cliente"]
    table.add_row([1, "Nome", cliente['nome']])
    table.add_row([2, "Email", utilizador['email']])
    table.add_row([3, "NIF", cliente['nif']])
    table.add_row([4, "Telemóvel", cliente['numero_telefone']])
    print(table)
    print(" \n * 5. Regressar")

    regressar = False
    opcao = 0
    while opcao < 1 or opcao > 5:
        opcao = int(input(" * \n * Escolha uma opção -> "))

        if opcao == 5:
            regressar = True

    if not regressar:

        if opcao == 1:
            novo_nome = input(" * Indique o novo nome -> ")
            atualizar_nome = """
                UPDATE utilizador
                SET nome = %s
                WHERE email = %s
            """
            cursor.execute(atualizar_nome, (novo_nome, utilizador['email']))
            connection.commit()

        elif opcao == 2:
            novo_email = input(" * Indique o novo email -> ")

            atualizar_email_cliente_query = """
                    UPDATE cliente
                    SET utilizador_email = NULL
                    WHERE utilizador_email = %s
                """
            cursor.execute(atualizar_email_cliente_query, (utilizador['email'],))

            atualizar_email = """
                UPDATE utilizador
                SET email = %s
                WHERE email = %s
            """
            cursor.execute(atualizar_email, (novo_email, utilizador['email']))
            connection.commit()

            atualizar_email_cliente = """
                UPDATE cliente
                SET utilizador_email = %s
                WHERE utilizador_email = %s
            """
            cursor.execute(atualizar_email_cliente, (novo_email, utilizador['email']))
            connection.commit()
            

        elif opcao == 3:
            novo_nif = int(input(" * Indique o novo NIF -> "))
            atualizar_nif = """
                UPDATE cliente
                SET nif = %s
                WHERE utilizador_email = %s
            """
            cursor.execute(atualizar_nif, (novo_nif, utilizador['email']))
            connection.commit()

        elif opcao == 4:
            novo_telefone = int(input(" * Indique o novo número de telemóvel -> "))
            atualizar_telefone = """
                UPDATE cliente
                SET numero_telefone = %s
                WHERE utilizador_email = %s
            """
            cursor.execute(atualizar_telefone, (novo_telefone, utilizador['email']))
            connection.commit()

        print(" * Atualização efetuada com sucesso!")   
        input(" * \n * Regressar - Enter")
    
    return regressar

# ------------------------------------
def efetuar_reserva(connection, utilizador):

    cursor = connection.cursor(cursor_factory = psycopg2.extras.DictCursor)

    date = datetime(year = 2024, month = 4, day = 16, hour = 0, minute = 0, second = 0)
    date_amanha = date + timedelta(days = 1)
    # substituir no execute
    # date = datetime.now(hour = 0, minute = 0, second = 0)

    # ir buscar reservas do dia de hoje
    fetch_reservas_hoje = """
        SELECT *
        FROM reserva
        WHERE horario >= %s AND horario < %s AND (estado = 'Reservado' OR estado = 'Em Espera')
        ORDER BY campo_id_campo, horario, estado DESC
    """

    # executar querys
    cursor.execute(fetch_reservas_hoje, (date, date_amanha))
    reservas_hoje = cursor.fetchall()
    
    os.system('cls')
    print(" ***** Reserva de campo no Padel Mondego *****\n *")
    #print(" * Campos Disponíveis para hoje,", datetime.now().strftime("%d/%m"))
    print(" * Campos para hoje, 16/04, HORAS (SÓ MOSTRAR A PARTIR DA HORA ATUAL)") # teste
    
    fetch_precos = "SELECT * FROM price WHERE ativo = True"
    cursor.execute(fetch_precos)
    precos = cursor.fetchall()
    print(" *\n * Preços *\n *")
    for preco in precos:
        print(f" * * {preco['tipo_dia']}, {preco['horario']} | {preco['preco_atual']} €")


    # listar todos os campos e todos os horários
    # estados: reservado; cancelado; finalizado; em espera; em espera cancelado; alterado reservado; alterado finalizado

    # ALTERAR ESTE ARRAY! ESSA É A SOLUÇÃO!
    horarios_semana = ["15h00", "16h30", "18h00", "19h30", "21h00", "22h30"]
    horarios_fds = ["10h00", "11h30", "13h00", "14h30", "16h00", "17h30", "19h00", "20h30"]

    hora_atual = datetime(year = 2024, month = 4, day = 16, hour = 12, minute = 00, second = 12)
    # hora_atual = datetime.now()

    horario = []
    # verificar se é fim de semana
    if hora_atual.isoweekday() >= 6:
        horario = horarios_fds
    else:
        horario = horarios_semana

    # mostrar slots a partir da hora atual
    horario = [horario[i] for i in range(len(horario)) if hora_atual.hour < int(horario[i][:2]) or (hora_atual.hour == int(horario[i][:2]) and hora_atual.minute <= int(horario[i][3:]))]

    print(" * \n * Campo - 1 * \n * ")
    i = 1
    count_slots_mostrados = 0
    for horario_semana in horario:
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
    for horario_semana in horario:
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
    for horario_semana in horario:
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

    opcao = 0
    nao_pode_fazer_reserva = False
    regressar = False
    while opcao < 1 or opcao > i + 1 or nao_pode_fazer_reserva:
        opcao = int(input(" *\n * Escolha uma opção -> "))

        campo_escolhido = 0
        # campo 1
        if opcao <= count_slots_mostrados:
            hora_escolhida = horario[opcao - 1]
            campo_escolhido = 1
        
        # campo 2
        elif opcao > count_slots_mostrados and opcao <= 2 * count_slots_mostrados:
            hora_escolhida = horario[opcao - (count_slots_mostrados - 1)]
            campo_escolhido = 2

        # campo 3
        elif opcao > 2 * count_slots_mostrados and opcao <= 3 * count_slots_mostrados:
            hora_escolhida = horario[opcao - (count_slots_mostrados * 2 - 1)]
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
        ORDER BY estado DESC, campo_id_campo, horario
    """

    cursor.execute(fetch_reservas_user, (utilizador['email'],))
    reservas_futuras = cursor.fetchall()

    os.system('cls')
    print(" ***** Reservas Futuras - Padel Mondego *****\n *")
    print(" * Neste menu é possível:")
    print(" * * Consultar as reservas atuais")
    print(" * * Cancelar uma reserva (escolher)")
    print(" * * Consultar reservas em espera\n ")
    
    i = 1
    table = PrettyTable()
    table.field_names = ["#", "Campo", "Data", "Horário", "Preço", "Estado"]

    reservas_a_alterar = []
    for reserva_futura in reservas_futuras:
        
        buscar_preco = """
            SELECT preco_atual
            FROM price 
            WHERE id_custo = %s
        """
        cursor.execute(buscar_preco, (reserva_futura['price_id_custo'],))
        preco = cursor.fetchone()[0]
        apresentar_preco = f"{preco} €"
        apresentar_i = f"{i}."
        if reserva_futura['estado'] == "Reservado" or reserva_futura['estado'] == "Em Espera":
            table.add_row([apresentar_i, reserva_futura['campo_id_campo'], reserva_futura['horario'].strftime("%d/%m"),
                        reserva_futura['horario'].strftime("%Hh%M"), apresentar_preco, reserva_futura['estado']])
            i += 1
            reservas_a_alterar.append(reserva_futura)

        else:
            table.add_row([" ", reserva_futura['campo_id_campo'], reserva_futura['horario'].strftime("%d/%m"),
                        reserva_futura['horario'].strftime("%Hh%M"), apresentar_preco, reserva_futura['estado']])

    print(table)

    print(f"\n * {i}. Regressar")

    opcao = 0
    while opcao < 1 or opcao > i:
        opcao = int(input(" * \n * Escolha uma opção -> "))

        if opcao == i:
            break
        
        elif opcao < i:
            id_reserva_cancelar = reservas_a_alterar[opcao - 1]['id_reserva']

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
    horario_atual = datetime(year = 2024, month = 4, day = 16, hour = 23, minute = 00, second = 00)

    fetch_historico_reservas = """
        SELECT horario, estado, price_id_custo, campo_id_campo, cliente_utilizador_email
        FROM reserva
        WHERE cliente_utilizador_email = %s AND horario < %s
        ORDER BY horario, campo_id_campo
    """
    cursor.execute(fetch_historico_reservas, [(utilizador['email'],), horario_atual])
    linhas = cursor.fetchall()

    os.system('cls')
    print(" ***** Hisórico de Reservas - Padel Mondego *****\n ")

    table = PrettyTable()
    table.field_names = ["Campo", "Data", "Horário", "Preço", "Estado"]

    for reserva_futura in linhas:

        buscar_preco = """
            SELECT preco_atual
            FROM price 
            WHERE id_custo = %s
        """
        cursor.execute(buscar_preco, (reserva_futura['price_id_custo'],))
        preco = cursor.fetchone()[0]
        apresentar_preco = f"{preco} €"

        table.add_row([reserva_futura['campo_id_campo'], reserva_futura['horario'].strftime("%d/%m"),
                        reserva_futura['horario'].strftime("%Hh%M"), apresentar_preco, reserva_futura['estado']])

    print(table)
    input("\n * Regressar - Enter")

# ------------------------------------
# retorna "Super Admin", "Admin", "Cliente" ou "Ambos"
def tipo_utilizador(connection, utilizador):

    tipo_user = None

    cursor = connection.cursor(cursor_factory = psycopg2.extras.DictCursor)

    fetch_ambos = """
        SELECT *
        FROM administrador AS a, cliente AS c
        WHERE c.utilizador_email = a.utilizador_email AND (c.utilizador_email = %s OR a.utilizador_email = %s)
    """
    cursor.execute(fetch_ambos, (utilizador['email'], utilizador['email']))
    linha1 = cursor.fetchone()

    if linha1 is not None:
        return "Ambos"

    fetch_admins = """
        SELECT *
        FROM administrador
        WHERE utilizador_email = %s
    """
    cursor.execute(fetch_admins, (utilizador['email'],))
    linha2 = cursor.fetchone()

    if linha2 is not None:
        if linha2['super_admin']:
            tipo_user = 'Super Admin'
        else:
            tipo_user = 'Admin'
    else:
        tipo_user = 'Cliente'

    return tipo_user

# ------------------------------------
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
        fetch_utilizadores = """ 
            SELECT email, passe, nome 
            FROM utilizador
            WHERE email = %s AND passe = %s
        """
        
        cursor.execute(fetch_utilizadores, (email, passe))
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
    if tipo_user == 'Ambos':
        tipo_user = 'Cliente e Admin'

    print(" * \n * Bem vindo,", tipo_user, nome)

    input(" * \n * Regressar - Enter")
    return utilizador

# ------------------------------------
def register(connection):
    os.system('cls')

    user = []

    print(" ***** Registar *****")
    print(" * \n * Registe os seus dados\n *")

    # adicionar whiles de segurança
    nome = input(" * Nome: ")

    cursor = connection.cursor(cursor_factory = psycopg2.extras.DictCursor)
    email_existe = True
    while email_existe:
        email = input(" * Email: ")

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
    insere_user = "INSERT INTO utilizador VALUES (%s, crypt(%s, gen_salt('bf')), %s)"
    cursor.execute(insere_user, user)
    connection.commit()

    print(" RETIRAR ISTO DEPOIS!!! ")
    print(" * \n * \n * Tipo de utilizador\n *")
    print(" * 1 - Admin")
    print(" * 2 - Cliente\n * ")

    tipo = int(input(" * Escolha uma opção -> "))

    if tipo == 1:

        user_admin = []

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

        insere_admin = "INSERT INTO administrador VALUES (%s, %s)"
        cursor.execute(insere_admin, user_admin)
        connection.commit()

        print(" * \n * \n * Registo efetuado com os dados acima indicados! * ")

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

        insere_admin = "INSERT INTO cliente VALUES (%s, %s, %s)"
        cursor.execute(insere_admin, user_cliente)
        connection.commit()

        print(" * \n * \n * Registo efetuado com os dados acima indicados! * ")

    input(" * Regressar - Enter")
    return user

# ------------------------------------
def apresentar_menu_admin(tipo_user, utilizador):
    os.system('cls')

    if tipo_user == 'Super Admin':
        print(" ***** Menu Super Admin", utilizador['nome'], "*****\n *")
    else:
        print(" ***** Menu Admin", utilizador['nome'], "*****\n *")
    print(" * 1 - Alterar Reservas")
    print(" * 2 - Alterar Preços")
    print(" * 3 - Estatísticas")
    print(" * 4 - Mensagem Geral")
    print(" * 5 - Mensagem Privada")
    
    if tipo_user == 'Admin':
        print(" * 6 - Logout | Sair\n *")
    else:
        print(" * 6 - Gestão de Admins")
        print(" * 7 - Logout | Sair\n *")

    opcao = 0
    while opcao < 1 or (opcao > 6 and tipo_user == 'Admin') or (opcao > 7 and tipo_user == 'Super Admin'):
        opcao = int(input(" * Escolha uma opção -> "))

    return opcao

# ------------------------------------
def apresentar_menu_cliente(utilizador):
    os.system('cls')
    print(" ***** Menu Cliente", utilizador['nome'], " *****\n *")
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
    os.system('cls')
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

    current_datetime = datetime(year = 2024, month = 4, day = 16, hour = 12, minute = 00, second = 00)
    diferenca = current_datetime - timedelta(hours = 1, minutes = 30)

    # dar update das reservas em que já passou 1h30
    # imaginemos -> jogo das 15h e são 16h50
    # 16h50 - 1h30 = 15h20; logo, horario (15h) < 15h20 
    update_jogos_a_decorrer = """
        UPDATE reserva
        SET estado = 'Finalizado'
        WHERE estado = 'Reservado' AND horario < %s
    """
    update_jogos_a_decorrer_alterados = """
        UPDATE reserva
        SET estado = 'Alterado Finalizado'
        WHERE estado = 'Alterado Reservado' AND horario < %s
    """

    cursor.execute(update_jogos_a_decorrer, (diferenca,))
    cursor.execute(update_jogos_a_decorrer_alterados, (diferenca,))
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