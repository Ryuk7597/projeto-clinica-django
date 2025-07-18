# projeto-clinica-django

Projeto da disciplina de Programação WEB II - Sistema de agendamento para uma clínica médica

Curso: Tecnologia em Análise e Desenvolvimento de Sistemas
Disciplina: Programação WEB II
Prof.: Victor Felix Arinos

## Conteúdo:
* Criar um projeto utilizando Django que deverá conter:
* 10 entidades;
* Pelo menos 2 Injeções de Dependência;
* 1 DER;
* 1 repositório no Github;
* 5 Testes automatizados com Katalon;
* 1 Script para build automática no Jenkins;
* 1 análise do código final com SonarCloud.


## Descrição do Projeto

Este projeto é uma aplicação web completa que simula um portal de agendamento e gerenciamento para uma clínica médica. 
Ele permite que pacientes se cadastrem, façam login e agendem consultas. Médicos e Administradores possuem painéis dedicados 
para gerenciar as operações da clínica, como horários, prontuários e cadastros de usuários.


## Funcionalidades Implementadas

* **Autenticação de Usuários:** Sistema completo de cadastro, login e logout com 3 perfis distintos (Paciente, Médico, Administrador).
* **Agendamento de Consultas:** Fluxo completo para o paciente visualizar médicos, verificar horários vagos e agendar uma consulta.
* **Painel do Paciente:** Área restrita para o paciente visualizar suas consultas agendadas.
* **Painel do Médico:** Área restrita para o médico visualizar suas consultas do dia e gerenciar prontuários (apenas o medico tem permissão de acesso para o gerenciamneto de prontuários).
* **Painel de Gerenciamento do Admin:** Um painel customizado (CRUD completo) para gerenciar todas as entidades do sistema:
    * Consultas
    * Médicos e Pacientes (incluindo suas contas de usuário)
    * Disponibilidades de Horários
    * Salas, Convênios e Especialidades.

## Testes automatizados com Katalon:
* 1 - Cadastro: Realiza o auto cadastro de um usuario teste do tipo paciente e realiza o login;
* 2 - Login: Realiza o login e o logout do usuario teste;
* 3 - Falha no login: Realiza a tentativa de login, porem com uma senha invalida;
* 4 - Agendamento: Realiza o auto agendamento de uma consulta com o usuario teste;
* 5 - Cadastrar medico: Realiza o login como admin (superuser), cadastra uma nova especialidade e cadastra um novo usuario do tipo medico.


## 2 Injeções de Dependência:
* 1° Injeção: enviar notificação a cada consulta agendada;
* 2° Injeção: enviar notificação quando o usuario criar uma conta.


## Usuarios
**Admin**: 
* user: admin; 
* senha: adminin123

**Paientes**
**User:**
* paciente1
* paciente2
**A senha para todos os usuarios é padrão (user123456)**

**Medico**
**User:**
* medico1
* medico2
**A senha para todos os usuarios é padrão (user123456)**
