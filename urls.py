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


from django.urls import path
from . import views

app_name = 'simulacoes'

urlpatterns = [
    path("", views.index, name="index"),
    path("simulacao/lancamento-projetil/", views.simulacao_projetil, name="simulacao_projetil"),
    path("simulacao/curva-aquecimento/", views.curva_aquecimento, name="curva_aquecimento"),
    path("simulacao/dilatacao-termica/", views.dilatacao_termica, name="dilatacao_termica"),
    path("simulacao/lei-gravitacao-universal-newton/", views.lei_gravitacao_universal_newton, name="lei_gravitacao_universal_newton"),
    # outros paths
]
