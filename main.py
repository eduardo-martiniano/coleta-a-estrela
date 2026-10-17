
import networkx as nx
import matplotlib.pyplot as plt
from itertools import combinations

# ============================================================
# 1. CONFIGURACAO DO MAPA
# ============================================================

G = nx.Graph()

# Malha urbana simulada: 6 x 6 cruzamentos.
# Cada aresta representa uma rua de distancia 1.
coordenadas = [
    (x, y)
    for x in range(6)
    for y in range(6)
]

for no in coordenadas:
    G.add_node(no, pos=no)

# Cria ruas horizontais e verticais
for x, y in coordenadas:
    for vizinho in [(x + 1, y), (x, y + 1)]:
        if vizinho in G:
            G.add_edge((x, y), vizinho, weight=1.0)

# Base do caminhao
base = (0, 0)

# Ecopontos numerados e suas localizacoes no mapa
ecopontos = {
    1: (2, 0),
    2: (5, 1),
    3: (4, 3),
    4: (1, 2),
    5: (0, 5),
    6: (3, 5),
    7: (5, 5),
    8: (2, 4),
}

# Todos os pontos que precisam ser conectados
pontos = [base] + list(ecopontos.values())


# ============================================================
# 2. HEURISTICA DO A*
# ============================================================

def heuristica(a, b):
    # Distancia Manhattan: movimentos horizontais e verticais
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


# ============================================================
# 3. A*: MENOR CAMINHO ENTRE DOIS PONTOS
# ============================================================

def calcular_caminho(origem, destino):
    caminho = nx.astar_path(
        G,
        origem,
        destino,
        heuristic=heuristica,
        weight="weight",
    )

    distancia = nx.path_weight(
        G, caminho, weight="weight"
    )

    return caminho, distancia


# ============================================================
# 4. CALCULA DISTANCIAS ENTRE TODOS OS PONTOS IMPORTANTES
# ============================================================

# A* calcula os menores caminhos entre base e ecopontos.
# A matriz resultante sera usada para otimizar a ordem de visita.

distancias = {}
caminhos = {}

for a, b in combinations(pontos, 2):
    caminho, distancia = calcular_caminho(a, b)

    distancias[(a, b)] = distancia
    distancias[(b, a)] = distancia

    caminhos[(a, b)] = caminho
    caminhos[(b, a)] = caminho[::-1]

    # Distancia do ponto para ele mesmo
    distancias[(a, a)] = 0.0
    caminhos[(a, a)] = [a]


# ============================================================
# 5. OTIMIZACAO GLOBAL DA ROTA
# ============================================================

# Programacao dinamica exata (Held-Karp).
# Testa estados formados pelos ecopontos ja visitados e
# pela posicao atual, sem precisar enumerar todas as rotas.
#
# Isso encontra a melhor ordem global para os pontos modelados.

ids = list(ecopontos.keys())
quantidade = len(ids)

# Cada estado e (mascara de visitados, ultimo ecoponto).
# Valor: (custo acumulado, ecoponto anterior).
dp = {}

# Inicializa rotas que saem da base e visitam um ecoponto
for i, id_ponto in enumerate(ids):
    mascara = 1 << i
    local = ecopontos[id_ponto]

    dp[(mascara, i)] = (
        distancias[(base, local)],
        None
    )

# Preenche os estados com mais ecopontos visitados
for tamanho in range(2, quantidade + 1):
    for grupo in combinations(range(quantidade), tamanho):
        mascara = sum(1 << i for i in grupo)

        for ultimo in grupo:
            mascara_anterior = mascara ^ (1 << ultimo)
            local_ultimo = ecopontos[ids[ultimo]]

            melhor_custo = float("inf")
            melhor_anterior = None

            for anterior in grupo:
                if anterior == ultimo:
                    continue

                estado_anterior = (
                    mascara_anterior, anterior
                )

                custo_anterior = dp[estado_anterior][0]
                local_anterior = ecopontos[ids[anterior]]

                custo = (
                    custo_anterior
                    + distancias[(local_anterior, local_ultimo)]
                )

                if custo < melhor_custo:
                    melhor_custo = custo
                    melhor_anterior = anterior

            dp[(mascara, ultimo)] = (
                melhor_custo,
                melhor_anterior
            )

# Escolhe o ultimo ecoponto considerando o retorno a base
mascara_completa = (1 << quantidade) - 1

melhor_custo_total = float("inf")
ultimo_escolhido = None

for ultimo in range(quantidade):
    custo_parcial = dp[(mascara_completa, ultimo)][0]
    local_ultimo = ecopontos[ids[ultimo]]

    custo_total = (
        custo_parcial + distancias[(local_ultimo, base)]
    )

    if custo_total < melhor_custo_total:
        melhor_custo_total = custo_total
        ultimo_escolhido = ultimo

# Reconstrói a ordem ótima
ordem_indices = []
mascara = mascara_completa
atual = ultimo_escolhido

while atual is not None:
    ordem_indices.append(atual)

    custo, anterior = dp[(mascara, atual)]
    mascara ^= 1 << atual
    atual = anterior

ordem_indices.reverse()
ordem_otima = [ids[i] for i in ordem_indices]


# ============================================================
# 6. MONTA A ROTA COMPLETA PELAS RUAS
# ============================================================

sequencia_pontos = (
    [base]
    + [ecopontos[i] for i in ordem_otima]
    + [base]
)

rota_completa = []
distancia_verificada = 0.0

for origem, destino in zip(
    sequencia_pontos[:-1],
    sequencia_pontos[1:]
):
    trecho = caminhos[(origem, destino)]

    if not rota_completa:
        rota_completa.extend(trecho)
    else:
        rota_completa.extend(trecho[1:])

    distancia_verificada += distancias[(origem, destino)]


# ============================================================
# 7. RESULTADOS NO TERMINAL
# ============================================================

print("\n============================================")
print(" ROTEIRIZACAO OTIMA DOS ECOPONTOS")
print("============================================")

print("\nOrdem ótima de visita:")
print("Base", end="")

for numero in ordem_otima:
    print(f" -> Ecoponto {numero}", end="")

print(" -> Base")

print("\n\nDetalhamento dos trechos:")

for origem, destino in zip(
    sequencia_pontos[:-1],
    sequencia_pontos[1:]
):
    if origem == base:
        nome_origem = "Base"
    else:
        nome_origem = f"Ecoponto {list(ecopontos.keys())[
            list(ecopontos.values()).index(origem)
        ]}"

    if destino == base:
        nome_destino = "Base"
    else:
        nome_destino = f"Ecoponto {list(ecopontos.keys())[
            list(ecopontos.values()).index(destino)
        ]}"

    print(
        f"{nome_origem} -> {nome_destino}: "
        f"{distancias[(origem, destino)]:.1f} unidades"
    )

print("\nDistancia total otima:", melhor_custo_total)
print("Distancia da rota reconstruida:", distancia_verificada)
print("Retorno a base: Sim")
print("Todos os ecopontos visitados:", len(ordem_otima))
print("Garantia: otimo para o grafo e os custos definidos.")


# ============================================================
# 8. VISUALIZACAO DO MAPA E DA ROTA
# ============================================================

pos = nx.get_node_attributes(G, "pos")

fig, ax = plt.subplots(figsize=(12, 10))

# Todas as ruas
nx.draw_networkx_edges(
    G,
    pos,
    ax=ax,
    edge_color="lightgray",
    width=1.5,
)

# Cruzamentos sem rótulos para reduzir a poluição visual
nx.draw_networkx_nodes(
    G,
    pos,
    ax=ax,
    node_color="white",
    edgecolors="gray",
    node_size=100,
)

# Ecopontos
nx.draw_networkx_nodes(
    G,
    pos,
    nodelist=list(ecopontos.values()),
    ax=ax,
    node_color="orange",
    edgecolors="black",
    node_size=650,
)

# Base
nx.draw_networkx_nodes(
    G,
    pos,
    nodelist=[base],
    ax=ax,
    node_color="green",
    edgecolors="black",
    node_size=900,
)

# Números dos ecopontos
rotulos = {
    local: str(numero)
    for numero, local in ecopontos.items()
}

nx.draw_networkx_labels(
    G,
    pos,
    labels=rotulos,
    ax=ax,
    font_size=10,
    font_weight="bold",
)

# Rota final
arestas_rota = list(
    zip(rota_completa[:-1], rota_completa[1:])
)

nx.draw_networkx_edges(
    G,
    pos,
    edgelist=arestas_rota,
    ax=ax,
    edge_color="blue",
    width=3.5,
)

# Destaca a base por cima da rota
nx.draw_networkx_nodes(
    G,
    pos,
    nodelist=[base],
    ax=ax,
    node_color="green",
    edgecolors="black",
    node_size=900,
)

# Exibe a ordem de visita ao lado de cada ecoponto
for ordem, numero in enumerate(ordem_otima, start=1):
    x, y = ecopontos[numero]

    ax.annotate(
        f"visita {ordem}",
        (x, y),
        xytext=(0, 17),
        textcoords="offset points",
        ha="center",
        fontsize=8,
        color="darkblue",
    )

ax.set_title(
    "Rota de menor distancia: todos os ecopontos e retorno a base",
    fontsize=13,
)

ax.text(
    0.5,
    -0.06,
    "Verde = Base | Laranja = Ecopontos | Azul = Rota | "
    f"Distancia total = {melhor_custo_total:.1f} unidades",
    transform=ax.transAxes,
    ha="center",
    fontsize=10,
)

ax.set_aspect("equal")
ax.axis("off")
plt.tight_layout()
plt.show()