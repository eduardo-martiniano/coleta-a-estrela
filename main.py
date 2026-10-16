
import networkx as nx
import matplotlib.pyplot as plt

# ============================================================
# 1. CRIACAO DO GRAFO E DEFINICAO DOS NOS
# ============================================================

G = nx.Graph()

# Coordenadas usadas para posicionar os nos no grafico.
# A malha e simulada e nao representa as ruas reais de Aracaju.

nodes = {
    "Base": (0, 0),

    "1": (1, 0),
    "2": (2, 0),
    "3": (3, 0),
    "4": (4, 0),
    "5": (5, 0),

    "6": (0, 1),
    "7": (1, 1),
    "8": (2, 1),
    "9": (3, 1),
    "10": (4, 1),
    "11": (5, 1),

    "12": (0, 2),
    "13": (1, 2),
    "14": (2, 2),
    "15": (3, 2),
    "16": (4, 2),
    "17": (5, 2),

    "18": (0, 3),
    "19": (1, 3),
    "20": (2, 3),
    "21": (3, 3),
    "22": (4, 3),
    "23": (5, 3),

    "24": (0, 4),
    "25": (1, 4),
    "26": (2, 4),
    "27": (3, 4),
    "28": (4, 4),
    "29": (5, 4),

    "30": (6, 4),
    "Ecoponto": (7, 4)
}

for node, position in nodes.items():
    G.add_node(node, pos=position)


# ============================================================
# 2. CRIACAO DAS RUAS
# ============================================================

# Conecta os nos vizinhos horizontalmente e verticalmente.
# Cada conexao representa um trecho de rua com custo 1.

for node1, (x1, y1) in nodes.items():
    for node2, (x2, y2) in nodes.items():

        if node1 == node2:
            continue

        distancia = abs(x1 - x2) + abs(y1 - y2)

        if distancia == 1:
            G.add_edge(
                node1,
                node2,
                weight=distancia
            )


# ============================================================
# 3. HEURISTICA DO A*
# ============================================================

def heuristic(node, goal):
    """
    Calcula a distancia Manhattan entre o no atual
    e o objetivo.

    Como a malha permite movimentos horizontais e verticais,
    essa heuristica e adequada para estimar a distancia restante.
    """

    x1, y1 = nodes[node]
    x2, y2 = nodes[goal]

    return abs(x1 - x2) + abs(y1 - y2)


# ============================================================
# 4. ALGORITMO A*
# ============================================================

def executar_a_star(origem, destino):

    caminho = nx.astar_path(
        G,
        origem,
        destino,
        heuristic=heuristic,
        weight="weight"
    )

    distancia = nx.astar_path_length(
        G,
        origem,
        destino,
        heuristic=heuristic,
        weight="weight"
    )

    return caminho, distancia


# ============================================================
# 5. DEFINICAO DOS PONTOS DE COLETA
# ============================================================

# O caminhao visitara os pontos na ordem definida abaixo.
# Nesta versao, a ordem ainda nao e otimizada automaticamente.

pontos_coleta = [
    "3",
    "7",
    "11",
    "14",
    "19",
    "22",
    "26",
    "29"
]

base = "Base"
destino_final = "Ecoponto"


# ============================================================
# 6. CALCULO DA ROTA COMPLETA
# ============================================================

posicao_atual = base

rota_completa = []
distancia_total = 0

print("\n==============================================")
print(" OTIMIZACAO DA ROTA DE COLETA DE RESIDUOS")
print(" Algoritmo: A*")
print(" Criterio: menor distancia")
print("==============================================\n")

print("Ordem dos pontos de coleta:")
print(" -> ".join(pontos_coleta))
print()

for ponto in pontos_coleta:

    caminho, distancia = executar_a_star(
        posicao_atual,
        ponto
    )

    print(f"Trecho: {posicao_atual} -> {ponto}")
    print(f"Caminho: {' -> '.join(caminho)}")
    print(f"Distancia: {distancia:.1f} unidades\n")

    if not rota_completa:
        rota_completa.extend(caminho)
    else:
        # Evita repetir o no que conecta dois trechos.
        rota_completa.extend(caminho[1:])

    distancia_total += distancia
    posicao_atual = ponto


# ============================================================
# 7. DESLOCAMENTO FINAL ATE O ECOPONTO
# ============================================================

caminho, distancia = executar_a_star(
    posicao_atual,
    destino_final
)

print(f"Trecho: {posicao_atual} -> {destino_final}")
print(f"Caminho: {' -> '.join(caminho)}")
print(f"Distancia: {distancia:.1f} unidades")

rota_completa.extend(caminho[1:])
distancia_total += distancia


# ============================================================
# 8. RESULTADO FINAL
# ============================================================

print("\n==============================================")
print(" RESULTADO FINAL")
print("==============================================")

print("\nRota completa do caminhao:")
print(" -> ".join(rota_completa))

print(f"\nPontos de coleta visitados: {len(pontos_coleta)}")
print(f"Movimentos realizados: {len(rota_completa) - 1}")
print(f"Distancia total: {distancia_total:.1f} unidades")

print("\nObservacao:")
print("As distancias sao unidades abstratas da malha.")
print("Elas nao representam quilometros reais.")


# ============================================================
# 9. VISUALIZACAO DA MALHA
# ============================================================

pos = nx.get_node_attributes(G, "pos")

plt.figure(figsize=(15, 10))


# ------------------------------------------------------------
# 9.1 Todas as ruas da malha
# ------------------------------------------------------------

nx.draw_networkx_edges(
    G,
    pos,
    edge_color="lightgray",
    width=1.8
)


# ------------------------------------------------------------
# 9.2 Nos comuns
# ------------------------------------------------------------

nos_comuns = [
    node for node in G.nodes()
    if node not in pontos_coleta
    and node != base
    and node != destino_final
]

nx.draw_networkx_nodes(
    G,
    pos,
    nodelist=nos_comuns,
    node_color="white",
    edgecolors="gray",
    node_size=500
)


# ------------------------------------------------------------
# 9.3 Pontos de coleta
# ------------------------------------------------------------

nx.draw_networkx_nodes(
    G,
    pos,
    nodelist=pontos_coleta,
    node_color="orange",
    edgecolors="black",
    node_size=750
)


# ------------------------------------------------------------
# 9.4 Base do caminhao
# ------------------------------------------------------------

nx.draw_networkx_nodes(
    G,
    pos,
    nodelist=[base],
    node_color="green",
    edgecolors="black",
    node_size=1000
)


# ------------------------------------------------------------
# 9.5 Ecoponto
# ------------------------------------------------------------

nx.draw_networkx_nodes(
    G,
    pos,
    nodelist=[destino_final],
    node_color="red",
    edgecolors="black",
    node_size=1100
)


# ------------------------------------------------------------
# 9.6 Numeros e nomes dos nos
# ------------------------------------------------------------

nx.draw_networkx_labels(
    G,
    pos,
    font_size=9,
    font_weight="bold"
)


# ------------------------------------------------------------
# 9.7 Rota calculada pelo A*
# ------------------------------------------------------------

arestas_rota = list(
    zip(
        rota_completa[:-1],
        rota_completa[1:]
    )
)

nx.draw_networkx_edges(
    G,
    pos,
    edgelist=arestas_rota,
    edge_color="blue",
    width=4
)


# ------------------------------------------------------------
# 9.8 Finalizacao do grafico
# ------------------------------------------------------------

plt.title(
    "Rota de coleta de residuos utilizando o algoritmo A*",
    fontsize=15
)

plt.figtext(
    0.5,
    0.02,
    "Verde: Base | Laranja: Pontos de coleta | "
    "Vermelho: Ecoponto | Azul: Rota do caminhao",
    ha="center",
    fontsize=10
)

plt.axis("equal")
plt.axis("off")
plt.tight_layout(rect=[0, 0.05, 1, 1])

plt.show()