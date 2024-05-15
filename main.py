import psycopg2
import psycopg2.extras
import os
import re
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
            print(" *\n * Até uma próxima! *")
            registar = True
            break

        if not registar:
            if tipo_user == "Ambos":
                
                os.system('cls')
                print(" * Pretende aceder como cliente ou administrador?\n *")
                print(" * 1. Cliente")
                print(" * 2. Administrador")

                while True:
                    opcao_menu = input(" * Escolha uma opção -> ").strip()
                    
                    if opcao_menu.isdigit():
                        opcao_menu = int(opcao_menu)
                        
                        if opcao_menu == 1:
                            tipo_user = "Cliente"
                            break
                        elif opcao_menu == 2:
                            tipo_user = "Admin"
                            break
                    print(" * \n *** ATENÇÃO -> Opção inválida! ***")

            if tipo_user == 'Admin' or tipo_user == 'Super Admin':
                menu_admin(connection, utilizador, tipo_user)
            else:
                menu_cliente(connection, utilizador)

# ------------------------------------
def menu_admin(connection, utilizador, tipo_user):
    
    opcao = 1 
    while opcao > 0 or opcao < 8:
        opcao = apresentar_menu_admin(tipo_user, utilizador)

        if opcao == 1:
            alterar_reservas_menu(connection)
        
        elif opcao == 2:
            alterar_precos(connection)

        elif opcao == 3:
            estatisticas(connection)
            
        elif opcao == 4:
            # o tipo user vai 'Admin' ou 'Super Admin'
            mensagens_admin(connection, utilizador, tipo_user)
        
        elif opcao == 5:
            descricao_campos(connection)

        elif opcao == 6:
            utilizador_novo = editar_perfil(connection, utilizador)
            utilizador = utilizador_novo

        elif opcao == 7 and tipo_user == 'Admin':
            os.system('cls')
            return None

        elif opcao == 7 and tipo_user == 'Super Admin':
            gestao_admins(connection)
            
        elif opcao == 8 and tipo_user == 'Super Admin':
            os.system('cls')
            return None

# ------------------------------------
def editar_perfil(connection, utilizador):

    cursor = connection.cursor(cursor_factory = psycopg2.extras.DictCursor)

    fetch_utilizador = """
        SELECT *
        FROM utilizador
        WHERE email = %s
    """
    cursor.execute(fetch_utilizador, (utilizador['email'],))
    utilizador_atual = cursor.fetchone()

    os.system('cls')
    print(" ***** Editar Perfil *****\n ")
    table = PrettyTable()
    table.field_names = ["#", "Tipo", "Info"]
    table.add_row([1, "Nome", utilizador_atual['nome']])
    table.add_row([2, "Password", "********"])
    print(table)
    print(" \n * 3. Regressar")

    while True:
        opcao = input("\n * Escolha uma opção -> ").strip()
        if opcao.isdigit():
            opcao = int(opcao)
            if 1 <= opcao <= 3:
                break
        print(" * \n *** ATENÇÃO -> Opção inválida! ***")

    if opcao == 1 or opcao == 2:
        novo_dado = input(" \n * \n * Novo dado -> ")

    if opcao == 1:
        alterar_nome = """
            UPDATE utilizador
            SET nome = %s
            WHERE email = %s
        """
        utilizador_atual['nome'] = novo_dado
        cursor.execute(alterar_nome, (novo_dado, utilizador_atual['email'],))
        connection.commit()
        print(" * Dados atualizados com sucesso!")

    elif opcao == 2:
        if novo_dado != utilizador_atual['passe']:
            cursor.execute("SELECT crypt(%s, gen_salt('bf'))", (novo_dado,))
            password_encriptada = cursor.fetchone()[0]
            alterar_password = """
                UPDATE utilizador
                SET passe = %s
                WHERE email = %s
            """
            utilizador_atual['passe'] = password_encriptada
            cursor.execute(alterar_password, (password_encriptada, utilizador_atual['email'],))
            connection.commit()
            print(" * Dados atualizados com sucesso!")
        else:
            print(" * A password é igual à anterior!")

    cursor.close()
    return utilizador_atual

# ------------------------------------
def descricao_campos(connection):

    cursor = connection.cursor(cursor_factory = psycopg2.extras.DictCursor)

    fetch_campos = """
        SELECT *
        FROM campo
    """
    cursor.execute(fetch_campos)
    campos = cursor.fetchall()

    os.system('cls')
    print(" ***** Descrição dos Campos *****\n *")
    table = PrettyTable()
    table.field_names = ["#", "Nome", "Descrição"]
    
    i = 1
    for campo in campos:
        table.add_row([i, campo['id_campo'], campo['descricao']])
        i += 1

    print(table)
    print(" \n *", i, "Regressar")

    while True:
        opcao = input("\n * Escolha uma opção -> ").strip()
        if opcao.isdigit():
            opcao = int(opcao)
            if 1 <= opcao <= i:
                break
        print(" * \n *** ATENÇÃO -> Opção inválida! ***")

    if opcao > 0 and opcao <= 3:
        campo = campos[opcao - 1]

        nova_descricao = input(" \n * Nova Descrição -> ")

        alterar_descricao = """
            UPDATE campo
            SET descricao = %s
            WHERE id_campo = %s
        """
        cursor.execute(alterar_descricao, (nova_descricao, campo['id_campo'],))
        connection.commit()

        print(" * Descrição alterada com sucesso!")
        cursor.close()
        input(" * \n * Regressar - Enter")

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

    table_admins = PrettyTable()
    table_admins.field_names = ["Nome", "Email"]
    for admin in admins:
        table_admins.add_row([admin['nome'], admin['email']])

    i = 1
    table = PrettyTable()
    table.field_names = ["#", "Nome", "Email"]
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
    print(" \n *", i, ". Registar um novo admin")
    print(" *", i + 1, ". Regressar\n *")

    opcao = 0
    novo = False
    regressar = False
    while opcao < 1 or opcao > i + 1:
        opcao = int(input(" * Escolha uma opção -> "))

        if opcao == i + 1:
            regressar = True
            break
        
        elif opcao == i:
            novo = True
            break

        elif opcao < i:
            cliente = cliente_valido[opcao - 1]
            email = cliente['email']
            break
    
    if not regressar:

        if novo:

            nome = input(" * Nome: ")
            padrao_email = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            
            while True:    
                email = input(" * Email: ")

                if not re.match(padrao_email, email):
                    print(" * \n *** ATENÇÃO -> Email inválido! ***")
                
                else:
                    try:
                        cursor.execute("SELECT email FROM utilizador WHERE email = %s", (email,))
                        if cursor.fetchone():
                            print(" * \n *** ATENÇÃO -> Email já registado! ***")
                        else:
                            break
                    except psycopg2.Error as e:
                        print(" * \n *** ERRO -> Falha ao verificar o email! ***")
                        print(e)

            passe = 'padel'

            # tem de ser por esta ordem!
            user = []
            user.append(email)
            user.append(passe)
            user.append(nome)

            try:
                cursor.execute("INSERT INTO utilizador (email, passe, nome) VALUES (%s, crypt(%s, gen_salt('bf', 8)), %s)", (user))
                connection.commit()

            except psycopg2.Error as e:
                connection.rollback()
                print(" * \n *** ERRO -> Falha ao inserir utilizador! ***")
                print(e)

        adicionar_admin = """
            INSERT INTO administrador (super_admin, utilizador_email)
            VALUES (%s, %s)
        """
        cursor.execute(adicionar_admin, (False, email,))
        connection.commit()

        print(" * Administrador adicionado com sucesso!")
        input(" * \n * Regressar - Enter")
    
    cursor.close()
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
    print(f"\n * {len(admins) + 1}. Regressar\n *")

    opcao = 0
    regressar = False
    while opcao < 1 or opcao > len(admins) + 1:
        opcao = int(input(" * Escolha um administrador -> "))

        if opcao == len(admins) + 1:
            regressar = True
            break
        
        elif opcao < len(admins) + 1:
            admin = admins[opcao - 1]
            break
    
    if not regressar:
        
        try:
            remover_mensagens_clientes = """
                DELETE FROM mensagem_cliente
                WHERE mensagem_id_mensagem IN (SELECT id_mensagem FROM mensagem WHERE administrador_utilizador_email = %s);
            """
            cursor.execute(remover_mensagens_clientes, (admin['email'],))

            remover_mensagens = """
                DELETE FROM mensagem
                WHERE administrador_utilizador_email = %s;
            """
            cursor.execute(remover_mensagens, (admin['email'],))

            remover_admin = """
                DELETE FROM administrador
                WHERE utilizador_email = %s;
            """
            cursor.execute(remover_admin, (admin['email'],))

            perceber_cliente = """
                SELECT COUNT(*)
                FROM cliente
                WHERE utilizador_email = %s;
            """
            cursor.execute(perceber_cliente, (admin['email'],))
            cliente = cursor.fetchone()

            if cliente[0] == 0:
                remover_utilizador = """
                    DELETE FROM utilizador
                    WHERE email = %s;
                """
                cursor.execute(remover_utilizador, (admin['email'],))
                
            connection.commit()
            input("")

            print(" *\n * Administrador removido com sucesso!")
            input(" * \n * Regressar - Enter")

        except (Exception, psycopg2.Error) as error:
            connection.rollback()
            print("Error:", error)

        finally:
            cursor.close()

    return regressar

# ------------------------------------
def estatisticas(connection):
    
    cursor = connection.cursor(cursor_factory = psycopg2.extras.DictCursor)
    
    os.system('cls')
    print(" ***** Estatísticas *****\n *")
    print(" * * Num determinado período (inclusivé),\n * ")
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

            count_horarios = {"15h00": 0, "16h30": 0, "18h00": 0, "19h30": 0, "21h00": 0, "22h30": 0, "10h00": 0, "11h30": 0,
                                "13h00": 0, "14h30": 0, "16h00": 0, "17h30": 0, "19h00": 0, "20h30": 0}

            for reserva in mais_horario_periodo:
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
            
            horarios_semana = ["15h00", "16h30", "18h00", "19h30", "21h00", "22h30"]
            horarios_fds = ["10h00", "11h30", "13h00", "14h30", "16h00", "17h30", "19h00", "20h30"]
            
            todos_horarios = []
            current_date = data_inicial
            while current_date <= data_final:
                
                if current_date.weekday() < 5:
                    for i in range(1, 4):
                        for horario in horarios_semana:
                            if not ja_reservado(connection, current_date, horario, i):
                                todos_horarios.append((current_date, horario, i))
                else:
                    for i in range(1, 4):
                        for horario in horarios_fds:
                            if not ja_reservado(connection, current_date, horario, i):
                                todos_horarios.append((current_date, horario, i))
                
                current_date += timedelta(days = 1)


            # Print timetables without reservations grouped by day and field
            os.system('cls')
            print(" ***** Campos sem reservas *****\n *")
            print(" * Período: (", data_inicial.strftime("%d/%m/%Y"), " a ", data_final.strftime("%d/%m/%Y"), ")\n ")

            table = PrettyTable()
            table.field_names = ["Data", "Horário", "Campo"]
            if todos_horarios:
                for horario in todos_horarios:
                    if horario[1] == "22h30" or horario[1] == "20h30":
                        table.add_row([horario[0].strftime("%d/%m"), horario[1], horario[2]], divider = True)
                    else:
                        table.add_row([horario[0].strftime("%d/%m"), horario[1], horario[2]])
                print(table)
            else:
                print(" * Todos os horários foram reservados neste período.\n *")

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
            tipo_menu = " ***** Receber notificação *****\n *"
            data_inicial, data_final = menu_periodo(tipo_menu)

            fetch_reservas_em_espera = """
                SELECT *
                FROM reserva
                WHERE horario >= %s AND horario <= %s AND estado = 'Em Espera'
                ORDER BY horario
            """
            cursor.execute(fetch_reservas_em_espera, (data_inicial, data_final))
            reservas_em_espera = cursor.fetchall()

            os.system('cls')
            print(" ***** Reservas em espera *****\n *")

            table = PrettyTable()
            table.field_names = ["Email Cliente", "Horário", "Campo"]
            for reserva in reservas_em_espera:
                table.add_row([reserva['cliente_utilizador_email'], reserva['horario'].strftime("%d/%m, %Hh%M"), reserva['campo_id_campo']])
            
            print(table)
            input(" \n * Regressar - Enter")
    
    cursor.close()

# ------------------------------------
def ja_reservado(connection, current_date, horario, campo_id):
    
    cursor = connection.cursor()
    
    slot = datetime.combine(current_date, datetime.strptime(horario, "%Hh%M").time())

    fetch_reservas = """
        SELECT COUNT(*)
        FROM reserva
        WHERE estado = 'Reservado' AND horario = %s AND campo_id_campo = %s;
    """
    
    cursor.execute(fetch_reservas, (slot, campo_id))
    count = cursor.fetchone()[0]
    cursor.close()

    return count > 0

# ------------------------------------
def mensagens_admin(connection, utilizador, tipo_user):

    opcao = 1
    while opcao > 0 and opcao < 3:
        os.system('cls')
        print(" ***** Mensagens *****\n *")
        print(" * 1. Enviar mensagem")
        print(" * 2. Histórico")
        print(" * 3. Regressar")
    
        opcao = int(input(" * \n * Escolha uma opção -> "))

        if opcao == 3:
            break

        elif opcao == 1:
            voltar = enviar_mensagem(connection, utilizador)
            if not voltar:
                opcao = 0

        elif opcao == 2:
            historico_mensagens(connection, utilizador, tipo_user)

# ------------------------------------
def historico_mensagens(connection, utilizador, tipo_user):

    cursor = connection.cursor(cursor_factory = psycopg2.extras.DictCursor)

    if tipo_user == 'Super Admin':
        fetch_mensagens = """
            SELECT *
            FROM mensagem
            ORDER BY administrador_utilizador_email, data_envio
        """
        cursor.execute(fetch_mensagens)
        mensagens = cursor.fetchall()

    elif tipo_user == 'Admin':
        fetch_mensagens = """
            SELECT *
            FROM mensagem
            WHERE administrador_utilizador_email = %s
        """
        cursor.execute(fetch_mensagens, (utilizador['email'],))
        mensagens = cursor.fetchall()
    
    else:
        print("erro")
        input(" ")

    os.system('cls')
    print(" ***** Histórico de Mensagens *****\n ")

    if tipo_user == 'Admin':
        table = PrettyTable()
        table.field_names = ["#", "Assunto", "Data Envio", "Geral"]
        
        for i, mensagem in enumerate(mensagens, start = 1):
            if mensagem['geral']:
                table.add_row([i, mensagem['assunto'], mensagem['data_envio'].strftime("%d/%m"), "Sim"])
            else:    
                table.add_row([i, mensagem['assunto'], mensagem['data_envio'].strftime("%d/%m"), "Não"])
        
        print(table)
        print(" \n *", i + 1, "Regressar\n *")

        opcao = 0
        while opcao < 1 or opcao > i + 1:
            opcao = int(input(" * \n * Escolha uma mensagem -> "))

            if opcao == i + 1:
                break

            elif opcao > 0 and opcao <= i:
                mensagem = mensagens[opcao - 1]

                os.system('cls')
                print(" ***** Mensagem *****\n *")
                print(" * Assunto: ", mensagem['assunto'])
                print(" * Data Envio: ", mensagem['data_envio'].strftime("%d/%m"))
                print(" * Conteúdo: ", mensagem['conteudo'])

                input(" * \n * Regressar - Enter")
    else:
        table = PrettyTable()
        table.field_names = ["#", "Remetente",  "Assunto", "Data Envio", "Geral"]
        for i, mensagem in enumerate(mensagens, start = 1):
            if mensagem['geral']:
                table.add_row([i, mensagem['administrador_utilizador_email'], mensagem['assunto'], mensagem['data_envio'].strftime("%d/%m"), "Sim"])
            else:
                table.add_row([i, mensagem['administrador_utilizador_email'], mensagem['assunto'], mensagem['data_envio'].strftime("%d/%m"), "Não"])
        
        print(table)
        print(" \n *", i + 1, "Regressar\n *")

        opcao = 0
        while opcao < 1 or opcao > i + 1:
            opcao = int(input(" * \n * Escolha uma mensagem -> "))

            if opcao == i + 1:
                break

            elif opcao > 0 and opcao <= i:
                mensagem = mensagens[opcao - 1]

                os.system('cls')
                print(" ***** Mensagem *****\n *")
                print(" * Remetente: ", mensagem['administrador_utilizador_email'])
                print(" * Assunto: ", mensagem['assunto'])
                print(" * Data Envio: ", mensagem['data_envio'].strftime("%d/%m"))
                print(" * Conteúdo: ", mensagem['conteudo'])

                input(" * \n * Regressar - Enter")
    
    cursor.close()

# ------------------------------------
def enviar_mensagem(connection, utilizador):

    cursor = connection.cursor(cursor_factory = psycopg2.extras.DictCursor)

    os.system('cls')
    print(" ***** Enviar Mensagem *****\n *")

    print(" * 1. Geral")
    print(" * 2. Cliente")
    print(" * 3. Regressar")

    opcao_mensagem = 0
    while opcao_mensagem < 1 or opcao_mensagem > 3:
        opcao_mensagem = int(input(" * \n * Escolha uma opção -> "))

        if opcao_mensagem == 1 or opcao_mensagem == 2:
            break

        elif opcao_mensagem == 3:
            return True

        else:
            print(" * \n * Opção inválida! * ")

    assunto = input(" \n * Assunto -> ")
    conteudo = input(" \n * Mensagem -> ")

    mensagem = []
    mensagem.append(assunto)
    mensagem.append(conteudo)

    data_hora = datetime.now().date()

    mensagem.append(data_hora)

    if opcao_mensagem == 1:
        mensagem.append(True)

    elif opcao_mensagem == 2:
        mensagem.append(False)

    mensagem.append(utilizador['email'])

    cursor.execute("SELECT nextval('mensagem_id_mensagem_seq')")
    id_correto = cursor.fetchone()[0]

    inserir_mensagem = """
        INSERT INTO mensagem (id_mensagem, assunto, conteudo, data_envio, geral, administrador_utilizador_email)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    cursor.execute(inserir_mensagem, (id_correto, mensagem[0], mensagem[1], mensagem[2], mensagem[3], mensagem[4]))
    connection.commit()

    fetch_clientes = """
        SELECT email, utilizador_email, nome
        FROM cliente, utilizador
        WHERE utilizador_email = email
    """
    cursor.execute(fetch_clientes)
    clientes = cursor.fetchall()

    # adicionar à tabela as mensagens GERAIS
    if opcao_mensagem == 1:

        for cliente in clientes:
            mensagem_cliente = []
            mensagem_cliente.append(False)
            mensagem_cliente.append(id_correto)
            mensagem_cliente.append(cliente['email'])

            inserir_mensagem_cliente = """
                INSERT INTO mensagem_cliente (lida, mensagem_id_mensagem, cliente_utilizador_email)
                VALUES (%s, %s, %s)
            """
            cursor.execute(inserir_mensagem_cliente, (mensagem_cliente))
            connection.commit()

    elif opcao_mensagem == 2:

        print(" \n * Escolha o cliente\n")
        table = PrettyTable()
        table.field_names = ["#", "Nome", "Email"]
        for i, cliente in enumerate(clientes, start = 1):
            table.add_row([i, cliente['nome'], cliente['email']])
        
        print(table)

        opcao_cliente = 0
        while opcao_cliente < 1 or opcao_cliente > len(clientes):
            opcao_cliente = int(input(" \n * Escolha um cliente -> "))

            if opcao_cliente > 0 and opcao_cliente <= len(clientes):
                break

            else:
                print(" * \n * Opção inválida! * ")

        mensagem_cliente = []
        mensagem_cliente.append(False)
        mensagem_cliente.append(id_correto)

        email_cliente = clientes[opcao_cliente - 1]['email']
        mensagem_cliente.append(email_cliente)

        inserir_mensagem_cliente = """
            INSERT INTO mensagem_cliente (lida, mensagem_id_mensagem, cliente_utilizador_email)
            VALUES (%s, %s, %s)
        """
        cursor.execute(inserir_mensagem_cliente, (mensagem_cliente))
        connection.commit()
        
    print(" * Mensagem enviada com sucesso!")
    input(" * \n * Regressar - Enter")
    cursor.close()
    return False

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
            input("\n * Regressar - Enter")
            
        elif opcao == 5:
            regressar = True
            break

    if not regressar:

        try:
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
            data_alteracao = datetime.now().date()
            atualizar_preco = """
                INSERT INTO price (id_custo, tipo_dia, horario, data_alteracao, ativo, valor_antigo, preco_atual)
                VALUES (nextval('price_id_custo_seq'), %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(atualizar_preco, (preco_a_alterar['tipo_dia'], preco_a_alterar['horario'],
                                            data_alteracao, True, preco_a_alterar['preco_atual'], novo_preco))

            # altera o anterior
            alterar_preco = """
                UPDATE price
                SET ativo = False
                WHERE id_custo = %s
            """
            cursor.execute(alterar_preco, (preco_a_alterar['id_custo'],))

            connection.commit()

        except (Exception, psycopg2.Error) as error:
            connection.rollback()
            print("Error:", error)

        finally:
            cursor.close()

        print(" * Preço atualizado com sucesso!")
        input(" * \n * Regressar - Enter")

# ------------------------------------
def alterar_reservas_menu(connection):

    cursor = connection.cursor(cursor_factory = psycopg2.extras.DictCursor)

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
    
    cursor.execute(fetch_reservas_futuras, (datetime.now(),))
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

    if not reservas_futuras:
        print(" * Não existem reservas futuras para alterar!")
        input(" * \n * Regressar - Enter")
        return

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
                    SET estado = 'Alterado Cancelado'
                    WHERE id_reserva = %s
                """
                cursor.execute(cancelar_reserva, (reserva_a_alterar['id_reserva'],))
                connection.commit()

                print(" * Reserva cancelada com sucesso!")
                input(" * \n * Regressar - Enter")

    cursor.close()

# ------------------------------------
def alterar_reservas(connection, reserva_a_alterar, reservas_futuras_corretas):
    
    cursor = connection.cursor(cursor_factory = psycopg2.extras.DictCursor)

    os.system("cls")
    print(" ***** Alterar Reserva *****\n *")
    print(" * Reserva a alterar:\n")
    
    table_reserva_a_alterar = PrettyTable()
    table_reserva_a_alterar.field_names = ["Cliente", "Email", "Horário", "Situação", "Preço", "Campo", "Estado"]
    apresentar_situacao = f"{reserva_a_alterar['tipo_dia']}, {reserva_a_alterar['p_horario']}"
    apresentar_preco = f"{reserva_a_alterar['preco_atual']} €"
    table_reserva_a_alterar.add_row([reserva_a_alterar['nome'], reserva_a_alterar['email'],
                reserva_a_alterar['r_horario'].strftime("%d/%m, %Hh%M"), apresentar_situacao,
                apresentar_preco, reserva_a_alterar['campo_id_campo'], reserva_a_alterar['estado']])
    print(table_reserva_a_alterar)

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
        table_outros_campos = PrettyTable()
        table_outros_campos.field_names = ["Cliente", "Email", "Horário", "Situação", "Preço", "Campo", "Estado"]
        for reserva_futura in reservas_futuras_corretas:
            if (reserva_futura['campo_id_campo'] != reserva_a_alterar['campo_id_campo']) and reserva_futura['r_horario'] == reserva_a_alterar['r_horario']:
                outros_campos.append(reserva_futura['campo_id_campo'])
                apresentar_situacao = f"{reserva_futura['tipo_dia']}, {reserva_futura['p_horario']}"
                apresentar_preco = f"{reserva_futura['preco_atual']} €"

                table_outros_campos.add_row([reserva_futura['nome'], reserva_futura['email'],
                            reserva_futura['r_horario'].strftime("%d/%m, %Hh%M"), apresentar_situacao,
                            apresentar_preco, reserva_futura['campo_id_campo'], reserva_futura['estado']], divider = True)
        
        if len(outros_campos) > 0:
            print(" *\n * Reservas noutros campos, à mesma hora:\n ")
            print(table_outros_campos)
        
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
            WHERE id_reserva = %s
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
        #hoje = datetime(year = 2024, month = 4, day = 16).day
        hoje = datetime.now().day

        outros_dias = []
        table_outros_dias = PrettyTable()
        table_outros_dias.field_names = ["Cliente", "Email", "Horário", "Situação", "Preço", "Campo", "Estado"]
        for reserva_futura in reservas_futuras_corretas:
            if reserva_futura['campo_id_campo'] == reserva_a_alterar['campo_id_campo'] and reserva_futura['r_horario'].strftime("%Hh%M") == reserva_a_alterar['r_horario'].strftime("%Hh%M") and reserva_futura['r_horario'].day != dia:
                outros_dias.append(reserva_futura['r_horario'].day)
                apresentar_situacao = f"{reserva_futura['tipo_dia']}, {reserva_futura['p_horario']}"
                apresentar_preco = f"{reserva_futura['preco_atual']} €"

                table_outros_dias.add_row([reserva_futura['nome'], reserva_futura['email'],
                            reserva_futura['r_horario'].strftime("%d/%m, %Hh%M"), apresentar_situacao,
                            apresentar_preco, reserva_futura['campo_id_campo'], reserva_futura['estado']], divider = True)

        if len(outros_dias) > 0:
            print(" *\n * Outras reservas, na mesma hora/campo:\n ")
            print(table_outros_dias)
        
        else:
            print(" * \n * Não há reservas noutros campos, nas mesmas situações * ")

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

        table_outras_horas = PrettyTable()
        table_outras_horas.field_names = ["#", "Horário", "Estado", "Cliente"]

        i = 1
        escolher_horario = []
        for horario_semana in horario:
            reservado = False
            for reserva_hoje in reservas_futuras_corretas:
                if reserva_hoje['campo_id_campo'] == reserva_a_alterar['campo_id_campo'] and reserva_hoje['r_horario'].strftime("%Hh%M") == horario_semana and reserva_hoje['r_horario'].day == reserva_a_alterar['r_horario'].day:
                    table_outras_horas.add_row([" ", horario_semana, reserva_hoje['estado'], reserva_hoje['email']])
                    reservado = True
                    break
            if not reservado:
                table_outras_horas.add_row([i, horario_semana, "Livre", " "])
                escolher_horario.append(horario_semana)
                i += 1

        if len(escolher_horario) > 0:
            print(" *\n * Horários disponíveis, no mesmo campo/dia *\n ")
            print(table_outras_horas, "\n")
        
        else:
            print(" * \n * Não há horários disponíveis, no mesmo campo/dia * ")

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
    
    cursor.close()

# ------------------------------------
def menu_cliente(connection, utilizador):

    opcao = 1
    while opcao > 0 or opcao < 6:
        opcao = apresentar_menu_cliente(connection, utilizador)

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
            mensagens_cliente(connection, utilizador)

        elif opcao == 6:
            os.system('cls')
            return None

# ------------------------------------
def mensagens_cliente(connection, utilizador):
    
    cursor = connection.cursor(cursor_factory = psycopg2.extras.DictCursor)

    regressar = False
    while not regressar:

        fetch_mensagens = """
            SELECT *
            FROM mensagem, mensagem_cliente
            WHERE id_mensagem = mensagem_id_mensagem AND cliente_utilizador_email = %s
            ORDER BY lida, mensagem_id_mensagem
        """
        cursor.execute(fetch_mensagens, (utilizador['email'],))
        mensagens = cursor.fetchall()

        count_lidas = 0
        count_gerais = 0
        count_privadas = 0
        count_notificacoes = 0
        for mensagem in mensagens:
            if not mensagem['lida']:
                count_lidas += 1
            elif mensagem['geral']:
                count_gerais += 1
            elif not mensagem['geral']:
                count_privadas += 1
            elif mensagem['assunto'] == "Campo Disponível!":
                count_notificacoes += 1
            else:
                print("Erro")
                input(" ")

        os.system('cls')
        print(" ***** Mensagens ***** \n *")

        i = 1
        mensagens_nao_lidas = []
        if count_lidas > 0:
            print(" * Não lidas *\n *")
            for mensagem in mensagens:
                if not mensagem['lida']:
                    print(f" * {i}. {mensagem['assunto']}, enviada a {mensagem['data_envio'].strftime('%d/%m')}")
                    i += 1
                    mensagens_nao_lidas.append(mensagem)
        else:
            print(" *\n * Não tem mensagens por ler *\n *")

        mensagens_gerais = []
        if count_gerais > 0:
            print(" *\n *\n * Mensagens do clube *\n *")
            for mensagem in mensagens:
                if mensagem['geral'] and mensagem['lida']:
                    print(f" * {i}. {mensagem['assunto']}, enviada a {mensagem['data_envio'].strftime('%d/%m')}")
                    i += 1
                    mensagens_gerais.append(mensagem)
        else:
            print(" *\n *\n * Não tem mensagens do clube *\n *")

        mensagens_privadas = []
        if count_privadas > 0:
            print(" *\n *\n * Mensagens do administrador *\n *")
            for mensagem in mensagens:
                if not mensagem['geral'] and mensagem['lida']:
                    fetch_admin = """
                        SELECT nome
                        FROM administrador, utilizador
                        WHERE utilizador_email = email AND utilizador_email = %s
                    """
                    cursor.execute(fetch_admin, (mensagem['administrador_utilizador_email'],))
                    nome_admin, = cursor.fetchone()
                    print(f" * {i}. {mensagem['assunto']}, enviada a {mensagem['data_envio'].strftime('%d/%m')}, por {nome_admin}")
                    i += 1
                    mensagens_privadas.append(mensagem)
        else:
            print(" *\n *\n * Não tem mensagens do administrador *\n *")

        notificacoes = []
        if count_notificacoes > 0:
            print(" *\n *\n * Notificações de Campo *\n *")
            for mensagem in mensagens:
                if mensagem['assunto'] == "Campo Disponível!":
                    print(f" * {i}. {mensagem['conteudo']}, enviada a {mensagem['data_envio'].strftime('%d/%m')}")
                    i += 1
                    notificacoes.append(mensagem)
        else:
            print(" *\n *\n * Não tem notificações de campo *\n *")

        print(" *", i, " - Regressar\n *")

        opcao = 0
        regressar = False
        while opcao < 1 or opcao > i:
            opcao = int(input(" * Escolha uma mensagem -> "))

            if opcao > 0 and opcao < i:
                if opcao <= count_lidas:
                    mensagem_escolhida = mensagens_nao_lidas[opcao - 1]

                elif opcao <= count_lidas + count_gerais:
                    mensagem_escolhida = mensagens_gerais[opcao - count_lidas - 1]

                elif opcao <= count_lidas + count_gerais + count_privadas:
                    mensagem_escolhida = mensagens_privadas[opcao - count_lidas - count_gerais - 1]

                elif opcao <= count_lidas + count_gerais + count_privadas + count_notificacoes:
                    mensagem_escolhida = notificacoes[opcao - count_lidas - count_gerais - count_privadas - 1]

            elif opcao == i:
                regressar = True
                break

            else:
                print(" * \n * Opção inválida! * ")

        if not regressar:

            fetch_admin = """
                SELECT nome
                FROM administrador, utilizador
                WHERE utilizador_email = email AND utilizador_email = %s
            """
            cursor.execute(fetch_admin, (mensagem['administrador_utilizador_email'],))
            nome_admin, = cursor.fetchone()

            os.system('cls')

            print(" ***** Mensagem *****\n *")
            print(" * De:", nome_admin, ", a", mensagem_escolhida['data_envio'].strftime("%d/%m/%Y"))
            print(" * Assunto:", mensagem_escolhida['assunto'])
            print(" * Mensagem:", mensagem_escolhida['conteudo'])

            if mensagem_escolhida['assunto'] == 'Campo Disponível!':
                print(" *\n * Para aceitar a reserva, diriga-se ao menu das suas reservas!")

            if mensagem_escolhida['lida'] == False:
                marcar_lida = """
                    UPDATE mensagem_cliente
                    SET lida = True
                    WHERE mensagem_id_mensagem = %s AND cliente_utilizador_email = %s
                """
                cursor.execute(marcar_lida, (mensagem_escolhida['mensagem_id_mensagem'], utilizador['email']))
                connection.commit()

            input(" * \n * Regressar - Enter")
        
    cursor.close()

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

    print(" \n ***** Descrição de Campos *****\n *")
    for campo in campos:
        print(" *", campo['descricao'])

    print("\n ***** Informações do Cliente *****\n")
    table = PrettyTable()
    table.field_names = ["#", "Info", "Cliente"]
    table.add_row([1, "Nome", cliente['nome']])
    table.add_row([2, "NIF", cliente['nif']])
    table.add_row([3, "Telemóvel", cliente['numero_telefone']])
    print(table)
    print(" \n * 4. Regressar")

    regressar = False
    opcao = 0
    while opcao < 1 or opcao > 4:
        opcao = int(input(" * \n * Escolha uma opção -> "))

        if opcao == 4:
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
            novo_nif = int(input(" * Indique o novo NIF -> "))
            atualizar_nif = """
                UPDATE cliente
                SET nif = %s
                WHERE utilizador_email = %s
            """
            cursor.execute(atualizar_nif, (novo_nif, utilizador['email']))
            connection.commit()

        elif opcao == 3:
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
    
    cursor.close()
    return regressar

# ------------------------------------
def efetuar_reserva(connection, utilizador):

    cursor = connection.cursor(cursor_factory = psycopg2.extras.DictCursor)

    # Lock à tabela reserva
    cursor.execute("SELECT * FROM reserva FOR UPDATE")

    data_para_reservas = datetime.now().replace(hour = 0, minute = 0, second = 0)
    
    opcao = 0
    regressar = False
    while opcao < 1 or opcao > i + 1:
        
        # opcao = i + 1
        opcao, i, hora_escolhida, campo_escolhido, reservas_hoje = apresentar_reservas(connection, utilizador, data_para_reservas)

        # outro dia
        if opcao == i:

            print(" * Selecione o dia que quer reservar *\n * ")  

            # dia de HOJE
            #hoje = datetime(year = 2024, month = 4, day = 16, hour = 0, minute = 0, second = 0).day
            hoje = datetime.now().day
            dias_seguintes = []

            contador = 1
            for j in range(0, 7):
                if data_para_reservas.replace(day = hoje + j).day != data_para_reservas.day:
                    print(" * ", contador , " - ", data_para_reservas.replace(day = hoje + j).strftime("%d/%m"))
                    dias_seguintes.append(data_para_reservas.replace(day = hoje + j))
                    contador += 1

            opcao_dia = 0
            regressar = False
            while opcao_dia < 1 or opcao_dia > contador:
                opcao_dia = int(input(" *\n * Escolha uma opção -> "))

                if opcao_dia < contador and opcao_dia > 0:
                    dia_escolhido = dias_seguintes[opcao_dia - 1]
                    break
                else:
                    print(" * \n * ATENÇÃO -> Opção inválida! * ")

            data_para_reservas = data_para_reservas.replace(day = dia_escolhido.day)
            opcao = 0
            
        # regressar
        elif opcao == i + 1:
            regressar = True
            break

    if not regressar:
    
        # efetuar reserva: "id_reserva, horario, estado, price_id_custo, campo_id_campo, cliente_utilizador_email"
        reserva_a_efetuar = []
        
        # hora escolhida
        hora_escolhida = datetime.strptime(hora_escolhida, "%Hh%M")
        # colocar a data de teste -> 16/04
        hora_escolhida = hora_escolhida.replace(year = data_para_reservas.year, month = data_para_reservas.month, day = data_para_reservas.day)
        
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
            print(" *\n * Ficará em espera para o slot: ", hora_escolhida.strftime("%d/%m"), " | ", hora_escolhida.strftime("%Hh%M"), " | Campo -", campo_escolhido)
            print(" * * Será notificado caso o campo fique vago! *")
        else:
            print(" *\n * A seguinte reserva foi efetuada: ", hora_escolhida.strftime("%d/%m"), " | ", hora_escolhida.strftime("%Hh%M"), " | ", preco_reserva, "€ | Campo -", campo_escolhido)

        efetua_reserva = """
            INSERT INTO reserva (id_reserva, horario, estado, price_id_custo, campo_id_campo, cliente_utilizador_email)
            VALUES (nextval('reserva_id_reserva_seq'), %s, %s, %s, %s, %s)
        """
        cursor.execute(efetua_reserva, reserva_a_efetuar)
        connection.commit()

        input(" *\n * \n * Regressar - Enter")

    cursor.close()

# ------------------------------------
def apresentar_reservas(connection, utilizador, data_para_reservas):

    cursor = connection.cursor(cursor_factory = psycopg2.extras.DictCursor)

    data_amanha = data_para_reservas + timedelta(days = 1)

    # ir buscar reservas do dia escolhido
    fetch_reservas_hoje = """
        SELECT *
        FROM reserva
        WHERE horario >= %s AND horario < %s AND (estado = 'Reservado' OR estado = 'Em Espera' OR estado = 'Alterado Reservado')
        ORDER BY campo_id_campo, horario, estado DESC
    """

    cursor.execute(fetch_reservas_hoje, (data_para_reservas, data_amanha))
    reservas_hoje = cursor.fetchall()
    
    os.system('cls')
    print(" ***** Reserva de campo no Padel Mondego *****\n *")
    print(" * Campos para", data_para_reservas.strftime("%d/%m"))
    
    fetch_precos = "SELECT * FROM price WHERE ativo = True"
    cursor.execute(fetch_precos)
    precos = cursor.fetchall()
    print(" *\n * Preços *\n *")
    for preco in precos:
        print(f" * * {preco['tipo_dia']}, {preco['horario']} | {preco['preco_atual']} €")

    # listar todos os campos e todos os horários
    # estados: reservado; cancelado; finalizado; em espera; em espera cancelado; alterado reservado; alterado finalizado

    horarios_semana = ["15h00", "16h30", "18h00", "19h30", "21h00", "22h30"]
    horarios_fds = ["10h00", "11h30", "13h00", "14h30", "16h00", "17h30", "19h00", "20h30"]

    horario = []
    # verificar se é fim de semana
    if data_para_reservas.isoweekday() >= 6:
        horario = horarios_fds
    else:
        horario = horarios_semana

    # agora sim, as horas que são neste momento 
    hora_atual = datetime.now()

    # mostrar slots a partir da hora atual
    horario = [horario[i] for i in range(len(horario)) if hora_atual.hour < int(horario[i][:2]) or (hora_atual.hour == int(horario[i][:2]) and hora_atual.minute <= int(horario[i][3:]))]

    print(" * \n * Campo - 1 * \n * ")
    i = 1
    count_slots_mostrados = 0
    for horario_semana in horario:
        reservado = False
        for reserva_hoje in reservas_hoje:
            if reserva_hoje['campo_id_campo'] == 1 and reserva_hoje['horario'].strftime("%Hh%M") == horario_semana:
                if reserva_hoje['estado'] == 'Reservado' or reserva_hoje['estado'] == 'Alterado Reservado':
                    print(" * ", i, " - ", horario_semana, " | ", reserva_hoje['estado'], " | ", reserva_hoje['cliente_utilizador_email'])
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
                if reserva_hoje['estado'] == 'Reservado' or reserva_hoje['estado'] == 'Alterado Reservado':
                    print(" * ", i, " - ", horario_semana, " | ", reserva_hoje['estado'], " | ", reserva_hoje['cliente_utilizador_email'])
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
                if reserva_hoje['estado'] == 'Reservado' or reserva_hoje['estado'] == 'Alterado Reservado':
                    print(" * ", i, " - ", horario_semana, " | ", reserva_hoje['estado'], " | ", reserva_hoje['cliente_utilizador_email'])
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
    while opcao < 1 or opcao > i + 1 or nao_pode_fazer_reserva:
        opcao = int(input(" *\n * Escolha uma opção -> "))

        campo_escolhido = 0
        hora_escolhida = ""
        # campo 1
        if opcao > 0 and opcao <= count_slots_mostrados:
            hora_escolhida = horario[opcao - 1]
            campo_escolhido = 1
        
        # campo 2
        elif opcao > count_slots_mostrados and opcao <= 2 * count_slots_mostrados:
            hora_escolhida = horario[opcao - (count_slots_mostrados + 1)]
            campo_escolhido = 2

        # campo 3
        elif opcao > 2 * count_slots_mostrados and opcao <= 3 * count_slots_mostrados:
            hora_escolhida = horario[opcao - (count_slots_mostrados * 2 + 1)]
            campo_escolhido = 3

        elif opcao < 1 or opcao > i + 1:
            print(" * \n * ATENÇÃO -> Opção inválida! *")
        
        # VOLTA A VERIFICAR SE PODE FAZER RESERVA
        # verificação que não reserva um campo já reservado
        # verificação que não fica em espera para um campo já em espera
        fetch_reservas_hoje = """
            SELECT *
            FROM reserva
            WHERE horario >= %s AND horario < %s AND (estado = 'Reservado' OR estado = 'Em Espera' OR estado = 'Alterado Reservado')
            ORDER BY campo_id_campo, horario, estado DESC
        """

        cursor.execute(fetch_reservas_hoje, (data_para_reservas, data_amanha))
        reservas_hoje = cursor.fetchall()

        for reserva_hoje in reservas_hoje:
            nao_pode_fazer_reserva = False
            if reserva_hoje['campo_id_campo'] == campo_escolhido and reserva_hoje['horario'].strftime("%Hh%M") == hora_escolhida:
                if reserva_hoje['cliente_utilizador_email'] == utilizador['email']:
                    if reserva_hoje['estado'] == 'Reservado' or reserva_hoje['estado'] == 'Alterado Reservado':
                        nao_pode_fazer_reserva = True
                        print(" * \n * ATENÇÃO -> Não pode reservar um campo que já reservou! * ")
                        break
                if reserva_hoje['cliente_utilizador_email'] != utilizador['email']:
                    if reserva_hoje['estado'] == 'Reservado' or reserva_hoje['estado'] == 'Alterado Reservado':
                        for res_hoje in reservas_hoje:
                            if res_hoje['horario'].strftime("%Hh%M") == hora_escolhida and res_hoje['cliente_utilizador_email'] == utilizador['email'] and res_hoje['campo_id_campo'] == campo_escolhido and res_hoje['estado'] == 'Em Espera':
                                print(" * \n * ATENÇÃO -> Já está em espera para este campo! * ")
                                nao_pode_fazer_reserva = True
                                break
                        if nao_pode_fazer_reserva:
                            break
        

    cursor.close()
    return opcao, i, hora_escolhida, campo_escolhido, reservas_hoje

# ------------------------------------
def reservas_atuais(connection, utilizador):

    cursor = connection.cursor(cursor_factory = psycopg2.extras.DictCursor)

    # hora teste
    #horario_atual = datetime(year = 2024, month = 4, day = 16, hour = 12, minute = 00, second = 00)
    horario_atual = datetime.now()

    # mostra reservas futuras
    fetch_reservas_user = """
        SELECT *
        FROM reserva
        WHERE cliente_utilizador_email = %s AND horario >= %s
        ORDER BY estado DESC, campo_id_campo, horario
    """

    cursor.execute(fetch_reservas_user, (utilizador['email'], horario_atual))
    reservas_futuras = cursor.fetchall()

    fetch_reservas_canceladas = """
        SELECT *
        FROM reserva
        WHERE horario >= %s AND cliente_utilizador_email != %s AND estado = 'Cancelado'
    """
    cursor.execute(fetch_reservas_canceladas, (horario_atual, utilizador['email']))
    reservas_canceladas = cursor.fetchall()

    os.system('cls')
    print(" ***** Reservas Futuras - Padel Mondego *****\n *")
    print(" * Neste menu é possível:")
    print(" * * Consultar as reservas atuais")
    print(" * * Cancelar uma reserva")
    print(" * * Consultar reservas em espera\n ")
    
    i = 1
    table = PrettyTable()
    table.field_names = ["#", "Campo", "Data", "Horário", "Preço", "Estado", "Not"]

    reservas_a_alterar = []
    reservas_em_espera = []
    apresentar_notificacao = " "
    continuar = False
    for reserva_futura in reservas_futuras:
        
        buscar_preco = "SELECT preco_atual FROM price WHERE id_custo = %s"
        cursor.execute(buscar_preco, (reserva_futura['price_id_custo'],))
        preco = cursor.fetchone()[0]
        apresentar_preco = f"{preco} €"
        apresentar_i = f"{i}."
        apresentar_notificacao = " "

        if reserva_futura['estado'] == "Reservado" or reserva_futura['estado'] == "Alterado Reservado":
            table.add_row([apresentar_i, reserva_futura['campo_id_campo'], reserva_futura['horario'].strftime("%d/%m"),
                        reserva_futura['horario'].strftime("%Hh%M"), apresentar_preco, reserva_futura['estado'], apresentar_notificacao])
            i += 1
            reservas_a_alterar.append(reserva_futura)
        
        elif reserva_futura['estado'] == 'Em Espera':
            continuar = False
            for res in reservas_canceladas:
                if res['horario'] == reserva_futura['horario'] and res['campo_id_campo'] == reserva_futura['campo_id_campo']:
                    reservas_em_espera.append(reserva_futura)
                    continuar = True
                    break

            if not continuar:
                table.add_row([apresentar_i, reserva_futura['campo_id_campo'], reserva_futura['horario'].strftime("%d/%m"),
                            reserva_futura['horario'].strftime("%Hh%M"), apresentar_preco, reserva_futura['estado'], apresentar_notificacao])
                reservas_a_alterar.append(reserva_futura)
                i += 1

        else:
            table.add_row([" ", reserva_futura['campo_id_campo'], reserva_futura['horario'].strftime("%d/%m"),
                        reserva_futura['horario'].strftime("%Hh%M"), apresentar_preco, reserva_futura['estado'], apresentar_notificacao])


    if table.rowcount != 0:
        print(table)
    else:
        print(" * Não tem reservas futuras! * ")

    table_2 = PrettyTable()
    table_2.field_names = ["#", "Campo", "Data", "Horário", "Preço", "Estado", "Not"]
    for reserva in reservas_em_espera:
        buscar_preco = "SELECT preco_atual FROM price WHERE id_custo = %s"
        cursor.execute(buscar_preco, (reserva['price_id_custo'],))
        preco = cursor.fetchone()[0]
        apresentar_preco = f"{preco} €"
        apresentar_i = f"{i}."
        apresentar_notificacao = "!"

        table_2.add_row([apresentar_i, reserva['campo_id_campo'], reserva['horario'].strftime("%d/%m"),
                        reserva['horario'].strftime("%Hh%M"), apresentar_preco, reserva['estado'], apresentar_notificacao])
        i += 1

    if reservas_em_espera != []:
        print(table_2)

    print(f"\n * {i}. Regressar")

    opcao = 0
    while opcao < 1 or opcao > i:
        opcao = int(input(" * \n * Escolha uma opção -> "))

        if opcao == i:
            break
        
        elif opcao < i:

            if opcao <= len(reservas_a_alterar):
                reserva_cancelar = reservas_a_alterar[opcao - 1]

                # estado fica "Cancelado"
                cancelar_reserva = """
                    UPDATE reserva
                    SET estado = 'Cancelado'
                    WHERE id_reserva = %s
                """
                cursor.execute(cancelar_reserva, (reserva_cancelar['id_reserva'],))
                connection.commit()

                # verifica se havia reservas em espera para o campo e hora cancelada
                reservas_totais = """
                    SELECT *
                    FROM reserva
                    WHERE estado = 'Em Espera' AND campo_id_campo = %s AND horario = %s
                """
                cursor.execute(reservas_totais, (reserva_cancelar['campo_id_campo'], reserva_cancelar['horario']))
                reservas = cursor.fetchall()

                fetch_mensagens = """
                    SELECT max(id_mensagem)
                    FROM mensagem
                """
                cursor.execute(fetch_mensagens)
                id_correto = cursor.fetchone()[0] + 1

                cliente_em_espera = []
                for reserva in reservas:
                    if reserva['campo_id_campo'] == reserva_cancelar['campo_id_campo'] and reserva['horario'] == reserva_cancelar['horario']:
                        conteudo_mensagem = f"A sua reserva 'Em Espera' para o campo {reserva['campo_id_campo']}, às {reserva['horario'].strftime('%Hh%M')}, no dia {reserva['horario'].strftime('%m-%d')} acabou de ficar disponível!"
                        cliente_em_espera.append(reserva['cliente_utilizador_email'])

                if len(cliente_em_espera) > 0:

                    try:
                        envia_notificacao = """
                            INSERT INTO mensagem (id_mensagem, assunto, conteudo, data_envio, geral, administrador_utilizador_email)
                            VALUES (%s, 'Campo Disponível!', %s, %s, FALSE, 'sadmin@gmail.com')
                        """
                        cursor.execute(envia_notificacao, (id_correto, conteudo_mensagem, horario_atual.strftime('%Y-%m-%d'),))

                        for cliente in cliente_em_espera:
                            envia_notificacao_cliente = """
                                INSERT INTO mensagem_cliente (lida, mensagem_id_mensagem, cliente_utilizador_email)
                                VALUES (FALSE, %s, %s)
                            """
                            cursor.execute(envia_notificacao_cliente, (id_correto, cliente))

                        connection.commit()
                        
                    except (Exception, psycopg2.Error) as error:
                        connection.rollback()
                        print("Error", error)

                    finally:
                        cursor.close()

                print(" * Reserva cancelada com sucesso!")

            elif opcao > len(reservas_a_alterar):
                reserva_opcao = reservas_em_espera[opcao - len(reservas_a_alterar) - 1]

                print(" * \n * 1. Aceitar Vaga * ")
                print(" * 2. Cancelar * ")

                opcao_reserva = 0
                while opcao_reserva < 1 or opcao_reserva > 2:
                    opcao_reserva = int(input(" * \n * Escolha uma opção -> "))

                    if opcao_reserva == 1:
                        aceitar_reserva = """
                            UPDATE reserva
                            SET estado = 'Reservado'
                            WHERE id_reserva = %s
                        """
                        cursor.execute(aceitar_reserva, (reserva_opcao['id_reserva'],))
                        connection.commit()
                        print(" * Reserva efetuada com sucesso!")

                    elif opcao_reserva == 2:
                        cancelar_reserva = """
                            UPDATE reserva
                            SET estado = 'Em Espera Cancelado'
                            WHERE id_reserva = %s
                        """
                        cursor.execute(cancelar_reserva, (reserva_opcao['id_reserva'],))
                        connection.commit()
                        print(" * Reserva cancelada com sucesso!")

                    else:
                        print(" * \n * Opção inválida! * ")

            input(" * \n * Regressar - Enter")

    cursor.close()

# ------------------------------------
def historico_reservas(connection, utilizador):
    
    cursor = connection.cursor(cursor_factory = psycopg2.extras.DictCursor)

    # hora teste
    #horario_atual = datetime(year = 2024, month = 4, day = 16, hour = 23, minute = 00, second = 00)
    horario_atual = datetime.now()

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

    if table.rowcount != 0:
        print(table)
    else:
        print(" * Não tem reservas no histórico! * ")
    
    input("\n * Regressar - Enter")
    cursor.close()

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

    if linha1:
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

    cursor.close()
    return tipo_user

# ------------------------------------
def login(connection):

    os.system('cls')
    print(" ***** Login *****")
    print(" * \n * Login com os seus dados\n *")

    while True:

        email_invalido = False
        passe_invalida = False
        padrao_email = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        email = str(123)
        while email.isdigit() or not email.strip() or not re.match(padrao_email, email):
            email = input(" * Email: ")
            if email.isdigit() or not email.strip() or not re.match(padrao_email, email):
                print("\n *** ATENÇÃO -> Input inválido ***")

        passe = str(123)
        while passe.isdigit() or not passe.strip():
            passe = input(" * Password: ")
            if passe.isdigit() or not passe.strip():
                print("\n *** ATENÇÃO -> Input inválido! ***")

        # fetch de utilizadores
        cursor = connection.cursor(cursor_factory = psycopg2.extras.DictCursor)
        fetch_utilizadores = """ 
            SELECT *
            FROM utilizador
            WHERE email = %s
        """
        cursor.execute(fetch_utilizadores, (email,))
        linha = cursor.fetchone()

        # verificar se o utilizador existe
        utilizador = []
        if linha is None:
            print(" * \n *** ATENÇÃO -> Utilizador não encontrado! ***")
            email_invalido = True
            continue

        cursor.execute("SELECT crypt(%s, passe) = passe FROM utilizador WHERE email = %s", (passe, email))
        
        if not cursor.fetchone()[0]:
            passe_invalida = True

        if email_invalido or passe_invalida:
            print(" * \n *** ATENÇÃO -> Um dos campos está inválido! ***")
            continue
        
        nome = linha['nome']
        utilizador = {'email': email, 'passe': passe, 'nome': nome}
        break

    print(" * \n * \n * Login efetuado com sucesso! * ")

    # verifica se é admin ou cliente
    tipo_user = tipo_utilizador(connection, utilizador)
    if tipo_user == 'Ambos':
        tipo_user = 'Cliente e Admin'

    print(" * \n * Bem vindo,", tipo_user, nome)

    input(" * \n * Regressar - Enter")
    cursor.close()
    return utilizador

# ------------------------------------
def register(connection):

    cursor = connection.cursor(cursor_factory = psycopg2.extras.DictCursor)
    user = []

    os.system('cls')
    print(" ***** Registar *****")
    print(" * \n * Registe os seus dados\n *")

    nome = input(" * Nome: ")

    padrao_email = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    while True:
        
        email = input(" * Email: ")
        
        if not re.match(padrao_email, email):
            print(" * \n *** ATENÇÃO -> Email inválido! ***")
        
        else:
            try:
                cursor.execute("SELECT email FROM utilizador WHERE email = %s", (email,))
                if cursor.fetchone():
                    print(" * \n *** ATENÇÃO -> Email já registado! ***")
                else:
                    break
            except psycopg2.Error as e:
                print(" * \n *** ERRO -> Falha ao verificar o email! ***")
                print(e)

    password = input(" * Password: ")
    cursor.execute("SELECT crypt(%s, gen_salt('bf'))", (password,))
    password_encriptada = cursor.fetchone()[0]

    # tem de ser por esta ordem!
    user.append(email)
    user.append(password_encriptada)
    user.append(nome)

    try:
        # Insert user data into the utilizador table
        cursor.execute("INSERT INTO utilizador (email, passe, nome) VALUES (%s, %s, %s)", (user))
        connection.commit()

    except psycopg2.Error as e:
        connection.rollback()
        print(" * \n *** ERRO -> Falha ao inserir utilizador! ***")
        print(e)
        return None

    user_cliente = []

    print(" * \n * ")

    nif = 0
    while True:
        nif = input(" * NIF: ")
        if len(nif) == 9 and nif.isdigit():
            try:
                cursor.execute("SELECT nif FROM cliente WHERE nif = %s", (nif,))
                if cursor.fetchone():
                    print(" * \n *** ATENÇÃO -> NIF já registado! ***")
                else:
                    break
            except psycopg2.Error as e:
                print(" * \n *** ERRO -> Falha ao verificar o NIF! ***")
                print(e)
        else:
            print("\n *** ATENÇÃO -> NIF inválido! ***")

    telemovel = 0
    while True:
        telemovel = input(" * Telemóvel: ")
        if len(telemovel) == 9 and telemovel.isdigit():
            try:
                cursor.execute("SELECT numero_telefone FROM cliente WHERE numero_telefone = %s", (telemovel,))
                if cursor.fetchone():
                    print(" * \n *** ATENÇÃO -> Número de telefone já registado! ***")
                else:
                    break
            except psycopg2.Error as e:
                print(" * \n *** ERRO -> Falha ao verificar o número de telefone! ***")
                print(e)
        else:
            print("\n *** ATENÇÃO -> telemovel inválido! ***")

    user_cliente.append(nif)
    user_cliente.append(telemovel)
    user_cliente.append(email)

    try:
        # Insert client data into the cliente table
        insere_cliente = "INSERT INTO cliente VALUES (%s, %s, %s)"
        cursor.execute(insere_cliente, user_cliente)
        connection.commit()

        print(" * \n * \n * Registo efetuado com os dados acima indicados! * ")

    except psycopg2.Error as e:
        connection.rollback()
        print(" * \n *** ERRO -> Falha ao inserir cliente! ***")
        print(e)
        input("ora bolas")
        return None

    input(" * Regressar - Enter")
    cursor.close()
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
    print(" * 4 - Mensagem")
    print(" * 5 - Descrição Campos")
    print(" * 6 - Editar Perfil")
    
    if tipo_user == 'Admin':
        print(" * 7 - Logout | Sair\n *")
    else:
        print(" * 7 - Gestão de Admins")
        print(" * 8 - Logout | Sair\n *")

    while True:
        opcao = input(" * Escolha uma opção -> ").strip()
        if opcao.isdigit():
            opcao = int(opcao)
            if (1 <= opcao <= 7 and tipo_user == 'Admin') or (1 <= opcao <= 8 and tipo_user == 'Super Admin'):
                return opcao
        print(" * \n *** ATENÇÃO -> Opção inválida! ***")

# ------------------------------------
def apresentar_menu_cliente(connection, utilizador):
    os.system('cls')
    print(" ***** Menu Cliente", utilizador['nome'], " *****\n *")
    print(" * 1 - Informações e Perfil")
    print(" * 2 - Reservar Campo")
    print(" * 3 - Reservas atuais")
    print(" * 4 - Histórico de Reservas")
    print(" * 5 - Mensagens")
    print(" * 6 - Logout | Sair\n *")

    cursor = connection.cursor(cursor_factory = psycopg2.extras.DictCursor)

    fetch_mensagens = """
        SELECT *
        FROM mensagem, mensagem_cliente
        WHERE id_mensagem = mensagem_id_mensagem 
                AND cliente_utilizador_email = %s 
                AND assunto = 'Campo Disponível!'
                AND lida = FALSE 
        ORDER BY lida, mensagem_id_mensagem
    """
    cursor.execute(fetch_mensagens, (utilizador['email'],))
    mensagens = cursor.fetchall()

    if len(mensagens) > 0:
        print(" *\n * Tem uma nova notificação de campo!\n *")

    while True:
        opcao = input(" * Escolha uma opção -> ").strip()
        if opcao.isdigit():
            opcao = int(opcao)
            if 1 <= opcao <= 6:
                return opcao
        print(" * \n *** ATENÇÃO -> Opção inválida! ***")

# ------------------------------------
def menu():
    os.system('cls')
    print(" ***** Padel Mondego *****\n")
    print(" * Bem Vindo à mais recente aplicação de reservas de campos de Padel")
    print(" * ")
    print(" * 1 - Login")
    print(" * 2 - Registar")
    print(" * 3 - Sair\n * ")

    while True:
        opcao = input(" * Escolha uma opção -> ").strip()
        if opcao.isdigit():
            opcao = int(opcao)
            if 1 <= opcao <= 3:
                return opcao
        print(" * \n *** ATENÇÃO -> Opção inválida! ***")

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

    cursor.close()

# ------------------------------------
def database_connection():
    print("Conexão com base de dados")

    try:
        connection = psycopg2.connect(
            user = "postgres",
            password = "pepas1206",
            host = "127.0.0.1",
            port = "5432",
            database = 'padel mondego'
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