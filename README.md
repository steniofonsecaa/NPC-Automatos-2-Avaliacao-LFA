

# NPC-Automatos-2-Avaliacao-LFA

**Projeto da segunda avaliação da disciplina de Linguagens Formais e Autômatos**
**Engenharia da Computação – UFMA (2025.1)**

---

## Índice

* [Visão Geral](#visão-geral)
* [Conteúdo do Repositório](#conteúdo-do-repositório)
* [Diagrama de Estados (AFD/AFN)](#diagrama-de-estados-afdafn)
* [Arkanoid Automato](#arkanoid-automato)
* [Apresentação (Slides)](#apresentação-slides)
* [Instalação e Uso](#instalação-e-uso)
* [Estrutura de Pastas](#estrutura-de-pastas)
* [Autores e Agradecimentos](#autores-e-agradecimentos)
* [Licença](#licença)

---

## Visão Geral

Este projeto reúne o trabalho da segunda avaliação da disciplina **Linguagens Formais e Autômatos** do curso de Engenharia da Computação da UFMA (2025.1). Nesta etapa, foram modelados e implementados autômatos finitos determinísticos (AFD) e não determinísticos (AFN) para diferentes NPCs (Non-Player Characters) em um cenário de jogo, além de um automato aplicado ao jogo **Arkanoid** e material de apresentação teórica.

## Conteúdo do Repositório

* **NPC/**: Modelos de autômatos para personagens do jogo, incluindo:

  * Vendedor (AFD)
  * Informante (AFD)/(AP)
  * Ferreiro (AFD)/(AFN)
* **Arkanoid/**: Automato que controla a lógica de estados no jogo Arkanoid.
* **Slide/**: Material de apresentação em formato de slides (PDF/PPT) sobre teoria de autômatos e aplicação prática.
* **Diagrams (\*.png)**: Imagens dos diagramas de estados para fácil visualização.

## Diagrama de Estados (AFD/AFN)

Em **NPC/** encontram-se os diagramas em PNG que representam as transições de estados para cada personagem:

* **npc\_vendedor\_afd.png**: Fluxo de negociação e vendas.
* **npc\_informante\_afd.png**: Estados de coleta e passagem de informação.
* **npc\_ferreiro\_afd.png**: Processo de forjamento e interação com o jogador.

> Para visualizar, abra as imagens em um visualizador de PNG ou incorpore-as em sua apresentação.

## Arkanoid Automato

A pasta **Arkanoid/** contém o diagrama de estados usado para governar:

* Posicionamento da barra
* Lançamento e rastreamento da bola
* Colisão com blocos e ativação de power-ups

Utilize esta definição para implementar a lógica de jogo em Python, JavaScript ou qualquer outra linguagem.

## Apresentação (Slides)

Na pasta **Slide/** está o material didático preparado com os seguintes tópicos:

1. Introdução a Autômatos Finito Determinístico (AFD)
2. Autômatos Finito Não Determinístico (AFN)
3. Equivalência e Transformações
4. Aplicações de NPCs em Jogos
5. Estudo de Caso: Arkanoid


## Estrutura de Pastas

```text
NPC-Automatos-2-Avaliacao-LFA/
├── NPC/
│   ├── npc_vendedor_afd.png
│   ├── npc_informante_afd.png
│   └── npc_ferreiro_afd.png
├── Arkanoid/
│   └── arkanoid_automato.png
├── Slide/
│   └── apresentação_autômatos.pdf
└── README.md
```




## Reconhecimentos e Direitos Autorais
@autor: Emanuel Lopes Silva e Stenio Fonseca 

@contato: emanuelsilva.slz@gmail.com

@data última versão: 10/06/2025

@versão: 1.0

@outros repositórios: https://github.com/EmanuelSilva69/NPC-Automatos-2-Avaliacao-LFA, https://github.com/EmanuelSilva69/Formigueiro-em-Netlogo, https://github.com/EmanuelSilva69/Rede-Neural-Material-Didatico-Inicializacao-de-Pesos

@Agradecimentos: Universidade Federal do Maranhão (UFMA), Professor Doutor
Thales Levi Azevedo Valente, e colegas de curso.

Copyright/License

Este material é resultado de um trabalho acadêmico para a disciplina
LINGUAGENS FORMAIS E AUTÔMATOS, sob a orientação do professor Dr.
THALES LEVI AZEVEDO VALENTE, semestre letivo 2025.1, curso Engenharia
da Computação, na Universidade Federal do Maranhão (UFMA). Todo o material
sob esta licença é software livre: pode ser usado para fins acadêmicos e comerciais
sem nenhum custo. Não há papelada, nem royalties, nem restrições de "copyleft" do
tipo GNU. Ele é licenciado sob os termos da Licença MIT, conforme descrito abaixo,
e, portanto, é compatível com a GPL e também se qualifica como software de código
aberto. É de domínio público. Os detalhes legais estão abaixo. O espírito desta
licença é que você é livre para usar este material para qualquer finalidade, sem
nenhum custo. O único requisito é que, se você usá-los, nos dê crédito.
Licenciado sob a Licença MIT. Permissão é concedida, gratuitamente, a qualquer
pessoa que obtenha uma cópia deste software e dos arquivos de documentação
associados (o "Software"), para lidar no Software sem restrição, incluindo sem
limitação os direitos de usar, copiar, modificar, mesclar, publicar, distribuir,
sublicenciar e/ou vender cópias do Software, e permitir pessoas a quem o Software
é fornecido a fazê-lo, sujeito às seguintes condições:
Este aviso de direitos autorais e este aviso de permissão devem ser incluídos em todas
as cópias ou partes substanciais do Software.
O SOFTWARE É FORNECIDO "COMO ESTÁ", SEM GARANTIA DE
QUALQUER TIPO, EXPRESSA OU IMPLÍCITA, INCLUINDO MAS NÃO SE
LIMITANDO ÀS GARANTIAS DE COMERCIALIZAÇÃO, ADEQUAÇÃO A UM
DETERMINADO FIM E NÃO INFRINGÊNCIA. EM NENHUM CASO OS
AUTORES OU DETENTORES DE DIREITOS AUTORAIS SERÃO
RESPONSÁVEIS POR QUALQUER RECLAMAÇÃO, DANOS OU OUTRA
RESPONSABILIDADE, SEJA EM AÇÃO DE CONTRATO, TORT OU OUTRA
FORMA, DECORRENTE DE, FORA DE OU EM CONEXÃO COM O
SOFTWARE OU O USO OU OUTRAS NEGOCIAÇÕES NO SOFTWARE.
Para mais informações sobre a Licença MIT: https://opensource.org/licenses/MIT
