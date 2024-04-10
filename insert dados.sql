-- tabela utilizador
INSERT INTO utilizador (email, passe, nome) VALUES
('afonso@gmail.com', 'password1', 'Afonso Jorge'),
('luis@gmail.com', 'password2', 'Luis Pedro'),
('admin@gmail.com', 'admin', 'Pedro Monteiro'),
('superadmin@gmail.com', 'superadmin', 'Maria Carolina');

-- tabela cliente
INSERT INTO cliente (nif, numero_telefone, utilizador_email) VALUES
(123456, 123456, 'afonso@gmail.com'),
(876543, 876543, 'luis@gmail.com');

-- tabela admin
INSERT INTO administrador (admin_id, super_admin, utilizador_email) VALUES
(1, TRUE, 'admin@gmail.com'),
(2, FALSE, 'superadmin@gmail.com');

-- tabela campo
INSERT INTO campo (id_campo, descricao) VALUES
(1, 'Campo 1'),
(2, 'Campo 2'),
(3, 'Campo 3');

-- tabela price
INSERT INTO price (id_custo, tipo_dia, horario, data_alteracao, ativo, valor_antigo, preco_atual) VALUES
(1, 'Dia de semana', 'Normal', '2024-04-08', TRUE, 30, 24),
(2, 'Dia de semana', 'Nobre', '2024-04-08', TRUE, 35, 30),
(3, 'Fim de semana', 'Normal', '2024-04-08', TRUE, 25, 20),
(4, 'Dia de semana', 'Normal', '2024-04-08', FALSE, 35, 30);

-- tabela reserva
INSERT INTO reserva (id_reserva, horario, estado, price_id_custo, campo_id_campo, cliente_utilizador_email) VALUES
(1, '2024-04-08 10:00:00', 'Reservado', 1, 1, 'afonso@gmail.com'),
(2, '2024-04-09 15:00:00', 'Finalizado', 2, 2, 'afonso@gmail.com'),
(3, '2024-04-01 10:00:00', 'Cancelado', 3, 3, 'afonso@gmail.com'),
(4, '2024-04-02 10:00:00', 'Finalizado', 4, 3, 'luis@gmail.com'),
(5, '2024-04-03 10:00:00', 'Em Espera', 1, 3, 'luis@gmail.com'),
(6, '2024-04-04 10:00:00', 'Em Espera Cancelado', 2, 1, 'luis@gmail.com'),
(7, '2024-04-04 10:00:00', 'Alterado Reservado', 3, 2, 'luis@gmail.com'),
(8, '2024-04-04 10:00:00', 'Alterado Finalizado', 4, 2, 'luis@gmail.com');

-- tabela mensagem
INSERT INTO mensagem (id_mensagem, assunto, conteudo, data_envio, administrador_utilizador_email) VALUES
(1, 'Promoção de Verão', 'Não percam as nossas promoções de verão!', '2024-04-08', 'admin@gmail.com'),
(2, 'Aviso de manutenção', 'O campo 2 estará fechado para manutenção na próxima semana!', '2024-04-09', 'admin@gmail.com');

-- tabela mensagem_cliente
INSERT INTO mensagem_cliente (lida, mensagem_id_mensagem, cliente_utilizador_email) VALUES
(TRUE, 1, 'afonso@gmail.com'),
(FALSE, 2, 'luis@gmail.com');

-- tabela admin_permissoes
INSERT INTO administrador_permissoes (administrador_utilizador_email) VALUES
('admin@gmail.com'),
('superadmin@gmail.com');

-- tabela permissoes
INSERT INTO permissoes (alterar_preco, alterar_reserva, cancelar_reserva, conceder_cliente, remover_cliente) VALUES
(TRUE, TRUE, TRUE, TRUE, TRUE),
(TRUE, TRUE, TRUE, FALSE, FALSE);