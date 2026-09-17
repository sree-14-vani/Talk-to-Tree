"""Talk to a Tree - Flask Application"""
import os
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_from_directory

from services.plant_service import get_plant_service
from services.chat_service import get_chat_service
from services.image_service import get_image_service

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = 'uploads'

plant_service = get_plant_service()
chat_service = get_chat_service()
image_service = get_image_service()


@app.route('/')
def index():
    """Home page"""
    plants = plant_service.get_all_plants()[:6]
    return render_template('index.html', featured_plants=plants, demo_mode=chat_service.is_demo_mode())


@app.route('/explore')
def explore():
    """Explore page with all plants"""
    plants = plant_service.get_all_plants()
    plant_types = sorted(set(p['plant_type'] for p in plants if p['plant_type']))
    return render_template('explore.html', plants=plants, plant_types=plant_types, demo_mode=chat_service.is_demo_mode())


@app.route('/plant/<plant_name>')
def plant_profile(plant_name):
    """Plant profile page"""
    plant_name = plant_name.replace('-', ' ')
    plant = plant_service.get_plant_by_name(plant_name)
    if not plant:
        return render_template('404.html', plant_name=plant_name), 404

    suggested_questions = chat_service.get_suggested_questions(plant_name)
    return render_template(
        'plant.html',
        plant=plant,
        all_plants=plant_service.get_all_plants(),
        suggested_questions=suggested_questions,
        demo_mode=chat_service.is_demo_mode()
    )


@app.route('/api/search')
def api_search():
    """Search plants"""
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({"plants": []})

    plants = plant_service.search_plants(query)
    return jsonify({"plants": plants[:10]})


@app.route('/api/chat', methods=['POST'])
def api_chat():
    """Chat with plant"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid request"}), 400

    question = data.get('question', '').strip()
    plant_name = data.get('plant_name')
    conversation_history = data.get('history', [])

    if not question:
        return jsonify({"error": "Question required"}), 400

    try:
        response = chat_service.ask(question, plant_name, conversation_history=conversation_history)
    except Exception:
        response = type('SafeResponse', (), {
            'answer': "I couldn't safely retrieve that plant information right now. Please ask about a plant in the local collection, or consult a qualified professional for medical guidance.",
            'sources': [],
            'demo_mode': True,
        })()

    return jsonify({
        "answer": response.answer,
        "sources": response.sources,
        "demo_mode": response.demo_mode
    })


@app.route('/api/translate', methods=['POST'])
def api_translate():
    """Translate narration using an optional Google Translate-backed helper."""
    data = request.get_json() or {}
    text = str(data.get('text', '')).strip()
    language = str(data.get('language', 'en-US')).strip().lower().split('-')[0]

    if not text:
        return jsonify({'error': 'Text required'}), 400
    if language == 'en':
        return jsonify({'text': text, 'translated': False})

    try:
        from deep_translator import GoogleTranslator
        translator = GoogleTranslator(source='auto', target=language)
        translated_parts = [
            translator.translate(text[start:start + 3500])
            for start in range(0, len(text), 3500)
        ]
        return jsonify({'text': ' '.join(translated_parts), 'translated': True})
    except Exception:
        return jsonify({
            'error': 'Translation is unavailable for this language in the current environment.',
            'text': text,
            'translated': False,
        }), 503


@app.route('/api/identify', methods=['POST'])
def api_identify():
    """Identify plant from image"""
    if 'image' not in request.files:
        return jsonify({"error": "No image provided"}), 400

    file = request.files['image']
    validation = image_service.validate_image(file)

    if not validation['valid']:
        return jsonify({"error": validation['error']}), 400

    image_path = image_service.save_image(file)
    identification = image_service.identify_plant(image_path)

    plant_name = identification['plant_name']
    plant = plant_service.get_plant_by_name(plant_name)

    return jsonify({
        "identification": identification,
        "plant": plant
    })


@app.route('/api/compare', methods=['POST'])
def api_compare():
    """Compare two plants"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid request"}), 400

    plant1 = data.get('plant1')
    plant2 = data.get('plant2')

    if not plant1 or not plant2:
        return jsonify({"error": "Both plant names required"}), 400

    comparison = plant_service.compare_plants(plant1, plant2)
    return jsonify(comparison)


@app.route('/api/fact')
def api_fact():
    """Get random nature fact"""
    fact = plant_service.get_random_fact()
    return jsonify(fact)


@app.route('/api/story/<plant_name>')
def api_story(plant_name):
    """Get knowledge story for plant"""
    response = chat_service.get_knowledge_story(plant_name)
    return jsonify({
        "story": response.answer,
        "sources": response.sources,
        "demo_mode": response.demo_mode
    })


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/health')
def health():
    """Health check"""
    return jsonify({
        "status": "ok",
        "demo_mode": chat_service.is_demo_mode(),
        "plants_count": len(plant_service.get_all_plants())
    })


@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)