-- dummy data insert

-- tabela utilizador
INSERT INTO utilizador (email, passe, nome) VALUES
('afonso@gmail.com', crypt('password1', gen_salt('bf', 8)), 'Afonso Jorge'),
('luis@gmail.com', crypt('password2', gen_salt('bf', 8)), 'Luis Pedro'),
('admin@gmail.com', crypt('admin', gen_salt('bf', 8)), 'Pedro Monteiro'),
('admin1@gmail.com', crypt('admin1', gen_salt('bf', 8)), 'Empregado 1'),
('admin2@gmail.com', crypt('admin2', gen_salt('bf', 8)), 'Empregado 2'),
('sadmin@gmail.com', crypt('sadmin', gen_salt('bf', 8)), 'Maria Carolina');

-- tabela cliente
INSERT INTO cliente (nif, numero_telefone, utilizador_email) VALUES
(123456789, 123456789, 'afonso@gmail.com'),
(987654321, 987654321, 'luis@gmail.com');

-- tabela admin
INSERT INTO administrador (super_admin, utilizador_email) VALUES
(TRUE, 'sadmin@gmail.com'),
(FALSE, 'admin@gmail.com'),
(FALSE, 'admin1@gmail.com'),
(FALSE, 'admin2@gmail.com');

-- tabela campo
INSERT INTO campo (id_campo, descricao) VALUES
(1, 'Campo 1 - Terra e Betão'),
(2, 'Campo 2 - Relva Sintética'),
(3, 'Campo 3 - Areia Azul');

-- tabela price

-- semana: 
-- -- 15h - 18h: 24€
-- -- 18h - 24h: 30€ 

-- fds: 20€
INSERT INTO price (id_custo, tipo_dia, horario, data_alteracao, ativo, valor_antigo, preco_atual) VALUES
(1, 'Dia de semana', 'Normal', '2024-04-08', TRUE, 30, 24),
(2, 'Dia de semana', 'Nobre', '2024-04-08', TRUE, 35, 30),
(3, 'Fim de semana', 'Normal', '2024-04-08', TRUE, 25, 20),
(4, 'Dia de semana', 'Normal', '2024-04-08', FALSE, 35, 30);

-- tabela reserva

-- semana: 15h - 24h: 
-- -- 15h/16h30, 16h30/18h, 18h/19h30, 19h30/21h, 21h/22h30, 22h30/24h

-- fds: 10h - 22h: 
-- -- 10h/11h30, 11h30/13h, 13h/14h30, 14h30/16h, 16h/17h30, 17h30/19h, 19h/20h30, 20h30/22h
INSERT INTO reserva (id_reserva, horario, estado, price_id_custo, campo_id_campo, cliente_utilizador_email) VALUES
(1, '2024-04-16 15:00:00', 'Reservado', 1, 1, 'afonso@gmail.com'),
(2, '2024-04-16 16:30:00', 'Reservado', 1, 1, 'afonso@gmail.com'),
(3, '2024-04-16 19:30:00', 'Reservado', 2, 3, 'afonso@gmail.com'),
(4, '2024-04-16 22:30:00', 'Reservado', 2, 3, 'luis@gmail.com'),
(5, '2024-04-03 10:00:00', 'Em Espera', 1, 3, 'luis@gmail.com'),
(6, '2024-04-04 10:00:00', 'Em Espera Cancelado', 2, 1, 'luis@gmail.com'),
(7, '2024-04-04 10:00:00', 'Alterado Reservado', 3, 2, 'luis@gmail.com'),
(8, '2024-04-04 10:00:00', 'Alterado Finalizado', 4, 2, 'luis@gmail.com');

-- tabela mensagem
INSERT INTO mensagem (id_mensagem, assunto, conteudo, data_envio, geral, administrador_utilizador_email) VALUES
(1, 'Promoção de Verão', 'Não percam as nossas promoções de verão!', '2024-04-08', FALSE, 'admin@gmail.com'),
(2, 'Aviso de manutenção', 'O campo 2 estará fechado para manutenção na próxima semana!', '2024-04-09', FALSE, 'admin1@gmail.com'),
(3, 'Aviso de chuva', 'O campo 2 estará molhado!', '2024-04-09', FALSE, 'admin1@gmail.com');

-- tabela mensagem_cliente
INSERT INTO mensagem_cliente (lida, mensagem_id_mensagem, cliente_utilizador_email) VALUES
(TRUE, 1, 'afonso@gmail.com'),
(FALSE, 2, 'luis@gmail.com'),
(FALSE, 3, 'afonso@gmail.com');

-- tabela admin_permissoes
INSERT INTO administrador_permissoes (administrador_utilizador_email) VALUES
('sadmin@gmail.com'),
('admin@gmail.com'),
('admin1@gmail.com'),
('admin2@gmail.com');