# Projeto: Simulações de Física com Python
# Autor: Ari Cardoso
# Licença: GNU General Public License v3.0
#
# Este programa é software livre: você pode redistribuí-lo e/ou modificá-lo
# sob os termos da Licença Pública Geral GNU conforme publicada pela Free Software Foundation,
# na versão 3 da licença.
#
# Este programa é distribuído na esperança de que seja útil,
# mas SEM QUALQUER GARANTIA; sem mesmo a garantia implícita de
# COMERCIALIZAÇÃO ou ADEQUAÇÃO A UM DETERMINADO PROPÓSITO.
# Veja a Licença Pública Geral GNU para mais detalhes.
#
# Você deve ter recebido uma cópia da Licença Pública Geral GNU
# junto com este programa. Se não, veja <https://www.gnu.org/licenses/>.
#

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_GET
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import io
from io import BytesIO
import base64

# Create your views here.


def index(request):
    return render(request, 'simulacoes/index.html', {})

def teste(request):
    return render(request, 'simulacoes/teste.html', {})

def simulation(request):
    return render(request, 'simulacoes/simulation.html', {})

def simulacao_projetil(request):
    # valores padrão
    velocidade = 20
    angulo = 45
    gravidade = 9.8

    if request.method == 'GET':
        # atualiza os parametros
        velocidade = float(request.GET.get('velocidade', velocidade))
        angulo = float(request.GET.get('angulo', angulo))
        gravidade = float(request.GET.get('gravidade', gravidade))

    # calculos da física
    angulo_rad = np.radians(angulo)
    tempo_total = 2 * velocidade * np.sin(angulo_rad) / gravidade
    # Alcance (distância total)
    alcance = (velocidade ** 2 * np.sin(2 * angulo_rad)) / gravidade
    
    # Altura máxima
    altura_maxima = (velocidade ** 2 * (np.sin(angulo_rad) ** 2) / (2 * gravidade))
    tempos = np.linspace(0, tempo_total, 100)
    x = velocidade * np.cos(angulo_rad) * tempos
    y = velocidade * np.sin(angulo_rad) * tempos - 0.5 * gravidade * tempos**2

    # geração do gráfico
    plt.figure()
    plt.plot(x, y, 'r-')
    plt.title('Trajetória do Projétil')
    plt.xlabel('Distância (m)')
    plt.ylabel('Altura (m)')
    plt.grid()
    # Adiciona texto no rodapé (coordenadas x, y são relativas à figura, entre 0 e 1)
    plt.figtext(0.5,                   # Posição horizontal (centralizada)
                0.01,                  # Posição vertical (próximo à base)
                f"Velocidade = {velocidade} m/s , Ângulo = {angulo}º , Gravidade = {gravidade} m/s²", 
                ha="center",           # Alinhamento horizontal ('center', 'left', 'right')
                fontsize=9, 
                color='gray')
    plt.tight_layout(rect=[0, 0.05, 1, 1])  # Ajusta automaticamente

    # Salva o gráfico em uma imagem
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    imagem_grafico = base64.b64encode(buffer.getvalue()).decode('utf-8')
    plt.close()

    #prepara resposta
    context = {
        'imagem_grafico': imagem_grafico,
        'velocidade': velocidade,
        'angulo': angulo,
        'gravidade': gravidade,
        'alcance': alcance,
        'altura_maxima': altura_maxima,
        'tempo_total': tempo_total,
    }

    return render(request, 'simulacoes/simulacao_projetil.html', context)

# Rota para API de simulação (retorna JSON para AJAX/frontend dinâmico)
@require_GET
def api_projetil(request):
    # valores padrão
    velocidade = 20
    angulo = 45
    gravidade = 9.8

    if request.method == 'GET':
        # atualiza os parametros
        velocidade = float(request.GET.get('velocidade', velocidade))
        angulo = float(request.GET.get('angulo', angulo))
        gravidade = float(request.GET.get('gravidade', gravidade))

    # calculos da física
    angulo_rad = np.radians(angulo)
    tempo_total = 2 * velocidade * np.sin(angulo_rad) / gravidade
    
    # Alcance (distância total)
    alcance = (velocidade ** 2 * np.sin(2 * angulo_rad)) / gravidade
    
    # Altura máxima
    altura_maxima = (velocidade ** 2 * (np.sin(angulo_rad) ** 2) / (2 * gravidade))

    tempos = np.linspace(0, tempo_total, 100)
    x = velocidade * np.cos(angulo_rad) * tempos
    y = velocidade * np.sin(angulo_rad) * tempos - 0.5 * gravidade * tempos**2

    # geração do gráfico
    plt.figure()
    plt.plot(x, y, 'r-')
    plt.title('Trajetória do Projétil')
    plt.xlabel('Distância (m)')
    plt.ylabel('Altura (m)')
    plt.grid()
    # Adiciona texto no rodapé (coordenadas x, y são relativas à figura, entre 0 e 1)
    plt.figtext(0.5,                   # Posição horizontal (centralizada)
                0.01,                  # Posição vertical (próximo à base)
                f"Velocidade = {velocidade} m/s , Ângulo = {angulo}º , Gravidade = {gravidade} m/s²", 
                ha="center",           # Alinhamento horizontal ('center', 'left', 'right')
                fontsize=9, 
                color='gray')
    plt.tight_layout(rect=[0.0, 0.05, 1.0, 1.0])  # Ajusta automaticamente

    # Salva o gráfico em uma imagem
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    imagem_grafico = base64.b64encode(buffer.getvalue()).decode('utf-8')
    plt.close()

    #prepara resposta
    context = {
        'imagem_grafico': imagem_grafico,
        'velocidade': velocidade,
        'angulo': angulo,
        'gravidade': gravidade,
        'alcance': alcance,
        'altura_maxima': altura_maxima,
        'tempo_total': tempo_total,
    }

    return JsonResponse(context)

def curva_aquecimento(request):
    # valores padrão
    massa = 100
    T0 = -20
    Tf = 120
    if request.method == 'GET':
        massa = float(request.GET.get('massa', massa))  # em gramas
        T0 = float(request.GET.get('temp_inicial', T0))  # em °C
        Tf = float(request.GET.get('temp_final', Tf))    # em °C

    # Constantes
    c_ice = 2.1     # J/g°C
    c_water = 4.18
    c_steam = 2.0
    Lf = 334        # J/g
    Lv = 2260       # J/g

    temp = []
    calor = []
    labels = []
    Q = 0

    # Etapas
    if T0 < 0:
        t1 = list(range(int(T0), 1))
        q1 = [massa * c_ice * (t - T0) for t in t1]
        q1 = [Q + q for q in q1]
        Q = q1[-1]
        temp += t1
        calor += q1
        labels += ['Sensível (Gelo)'] * len(t1)

    if T0 <= 0 < Tf:
        temp += [0, 0]
        calor += [Q, Q + massa * Lf]
        Q = calor[-1]
        labels += ['Latente (Fusão)'] * 2

    if T0 <= 0 < Tf:
        t3 = list(range(1, min(101, int(Tf) + 1)))
        q3 = [Q + massa * c_water * (t - 0) for t in t3]
        Q = q3[-1] if q3 else Q
        temp += t3
        calor += q3
        labels += ['Sensível (Líquido)'] * len(t3)

    if Tf > 100:
        temp += [100, 100]
        calor += [Q, Q + massa * Lv]
        Q = calor[-1]
        labels += ['Latente (Vaporização)'] * 2

        t5 = list(range(101, int(Tf) + 1))
        q5 = [Q + massa * c_steam * (t - 100) for t in t5]
        temp += t5
        calor += q5
        labels += ['Sensível (Vapor)'] * len(t5)

    # Gráfico
    sns.set(style='whitegrid', palette='muted')
    plt.figure(figsize=(10, 6))

    colors = {
        'Sensível (Gelo)': '#1f77b4',
        'Latente (Fusão)': '#ff7f0e',
        'Sensível (Líquido)': '#2ca02c',
        'Latente (Vaporização)': '#d62728',
        'Sensível (Vapor)': '#9467bd'
    }

    for stage in set(labels):
        indices = [i for i, label in enumerate(labels) if label == stage]
        plt.plot([temp[i] for i in indices], [calor[i] for i in indices],
                    label=stage, color=colors[stage], linewidth=2)

    plt.xlabel("Temperatura (°C)")
    plt.ylabel("Calor (J)")
    plt.title("Curva de Aquecimento da Água")
    plt.legend(title="Tipo de Calor")
    plt.tight_layout()

    # Converter para base64
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    imagem_grafico = base64.b64encode(buf.read()).decode("utf-8")
    buf.close()

    return render(request, 'simulacoes/curva_aquecimento.html', {
        'imagem_grafico': imagem_grafico,
        'massa': massa,
        'temp_inicial': T0,
        'temp_final': Tf,
        'energia_total': round(Q, 2)  # total em J
    })

