from flask import Flask, jsonify, request
import pandas as pd
import json
from unidecode import unidecode
import os

app = Flask(__name__)

# Carregar dados na memória
def load_data():
    # Carregar JSON
    with open('selfit-mar-aberto.json', 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    
    # Carregar planilha
    df = pd.read_excel('Lista de unidades e denrerecos e links para o flows Selfit (1) (1).xlsx')
    
    # Criar dicionários para acesso rápido
    estados = {}
    cidades = {}
    unidades = {}
    
    # Processar dados da planilha
    for _, row in df.iterrows():
        estado = row['ESTADO'].strip()
        cidade = row['CIDADE'].strip()
        unidade = row['UNIDADE'].strip()
        endereco = row['ENDEREÇO']
        link = row['Links']
        
        # Adicionar estado
        if estado not in estados:
            estados[estado] = {
                'id': unidecode(estado).replace(' ', '_'),
                'title': estado
            }
        
        # Adicionar cidade
        if estado not in cidades:
            cidades[estado] = set()
        cidades[estado].add(cidade)
        
        # Adicionar unidade
        if cidade not in unidades:
            unidades[cidade] = []
        
        unidades[cidade].append({
            'id': unidecode(unidade).replace(' ', '_'),
            'title': unidade,
            'description': endereco,
            'link': link
        })
    
    return json_data, estados, cidades, unidades

# Carregar dados na inicialização
json_data, estados, cidades, unidades = load_data()

@app.route('/estados', methods=['GET'])
def get_estados():
    return jsonify([
        {"id": info['id'], "title": info['title']}
        for info in estados.values()
    ])

@app.route('/cidades', methods=['GET'])
def get_cidades():
    estado_param = request.args.get('estado')
    if not estado_param:
        return jsonify({'error': 'Parâmetro estado é obrigatório'}), 400

    # Função de normalização
    def norm(s):
        return unidecode(str(s)).replace(' ', '_').lower().strip()

    estado_param_norm = norm(estado_param)

    # Procurar pelo estado normalizado
    estado_nome = None
    for nome, info in estados.items():
        if norm(info['id']) == estado_param_norm or norm(nome) == estado_param_norm:
            estado_nome = nome
            break

    if not estado_nome or estado_nome not in cidades:
        return jsonify({'error': 'Estado não encontrado'}), 404

    return jsonify([
        {"id": unidecode(cidade).replace(' ', '_'), "title": cidade}
        for cidade in sorted(cidades[estado_nome])
    ])

@app.route('/unidades', methods=['GET'])
def get_unidades():
    estado_param = request.args.get('estado')
    cidade_param = request.args.get('cidade')
    
    if not estado_param or not cidade_param:
        return jsonify({'error': 'Parâmetros estado e cidade são obrigatórios'}), 400
    
    # Função de normalização
    def norm(s):
        return unidecode(str(s)).replace(' ', '_').lower().strip()

    estado_param_norm = norm(estado_param)
    cidade_param_norm = norm(cidade_param)

    # Procurar pelo estado normalizado
    estado_nome = None
    for nome, info in estados.items():
        if norm(info['id']) == estado_param_norm or norm(nome) == estado_param_norm:
            estado_nome = nome
            break
    if not estado_nome or estado_nome not in cidades:
        return jsonify({'error': 'Estado não encontrado'}), 404

    # Procurar pela cidade normalizada
    cidade_nome = None
    for cidade in cidades[estado_nome]:
        if norm(cidade) == cidade_param_norm:
            cidade_nome = cidade
            break
    if not cidade_nome or cidade_nome not in unidades:
        return jsonify({'error': 'Cidade não encontrada'}), 404

    return jsonify(sorted(unidades[cidade_nome], key=lambda x: x['title']))

@app.route('/link', methods=['GET'])
def get_link():
    unidade = request.args.get('unidade')
    if not unidade:
        return jsonify({'error': 'Parâmetro unidade é obrigatório'}), 400
    
    # Procurar o link em todas as unidades
    for cidade_unidades in unidades.values():
        for u in cidade_unidades:
            if u['id'] == unidade:
                return jsonify({
                    "link": u['link'],
                    "title": u['title'],
                    "description": u['description']
                })
    
    return jsonify({'error': 'Unidade não encontrada'}), 404

if __name__ == '__main__':
    # Usa a porta do Glitch se disponível, senão usa 5001
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port) 