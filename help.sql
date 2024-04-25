
-- funções
CREATE [OR REPLACE] FUNCTION nome(argNome argTipo,...)
RETURNS tipo AS $$
	DECLARE
		-- declaracoes
	BEGIN
		-- instruções
		RETURN valor;
	END;
$$ LANGUAGE plpgsql;

-- triggers -> programa associado a uma tabela que é executado automaticamente quando ocorre um evento
-- seja inserir, apagar ou atualizar um registo

-- valores no trigger: new (INSERT/UPDATE) ou old (UPDATE/DELETE)
CREATE TRIGGER name { BEFORE | AFTER} { event [ OR ... ] }
	ON table_name
	[ FOR [ EACH ] { ROW | STATEMENT } ]
	[ WHEN ( condition ) ]
	EXECUTE FUNCTION function_name()

CREATE OR REPLACE FUNCTION registo() 
RETURNS trigger AS $$
	DECLARE
		j integer;
	BEGIN
		select count(*) from users into j;
		insert into contagem values (j);
		RETURN new;
	END;
$$ LANGUAGE plpgsql;	


-- criar tabela
CREATE TABLE cliente (
	nif		 NUMERIC(8,2),
	numero_telefone	 NUMERIC(8,2),
	utilizador_email VARCHAR(512),
	PRIMARY KEY(utilizador_email)
);

-- inserir valores
INSERT INTO mensagem_cliente (lida, mensagem_id_mensagem, cliente_utilizador_email) 
VALUES 
	(TRUE, 1, 'afonso@gmail.com'),
	(FALSE, 2, 'luis@gmail.com');

-- eliminar tabela
DROP TABLE nome_da_tabela;

-- funções de grupo
SELECT COUNT(*), SUM(idade), AVG(idade), MAX(idade), MIN(idade)

-- atualizar registos
UPDATE nome_da_tabela
SET 
	coluna = valor,
	coluna = valor,
WHERE condição;

-- apagar registos
DELETE FROM nome_da_tabela
WHERE condição;