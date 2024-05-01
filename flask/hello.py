from flask import Flask, render_template, request
import sqlite3
#from flask import request

app = Flask(__name__)

def float_format(value, format_spec="0.2f"):
    return format(value, format_spec)

app.jinja_env.filters['floatformat'] = float_format

def get_db_connection():
    conn = sqlite3.connect('pankegg.db')
    conn.row_factory = sqlite3.Row
    return conn

# @app.route('/')
# def show_bins():
#     conn = get_db_connection()
#     cur = conn.cursor()
#     cur.execute("SELECT * FROM bin")
#     bins = cur.fetchall()
#     conn.close()
#     return render_template('show_bins.html', bins=bins)

@app.route('/bin_query')
def show_bins2():
    # Obtenir les colonnes demandées, sinon utiliser un ensemble par défaut
    requested_columns = request.args.getlist('columns')
    print(requested_columns)
    default_columns = ['id', 'bin_name', 'completeness', 'contamination', 'taxonomic_id']
    columns = requested_columns if requested_columns else default_columns

    # Construire une requête SQL sécurisée en vérifiant que chaque colonne demandée est valide
    safe_columns = [col for col in columns if col in default_columns]
    if not safe_columns:
        safe_columns = default_columns  # Utiliser les colonnes par défaut si aucune colonne demandée n'est valide

    conn = get_db_connection()
    cur = conn.cursor()
    query = f"SELECT {', '.join(safe_columns)} FROM bin"
    print(query)
    cur.execute(query)
    bins = cur.fetchall()
    #print(bins)
    conn.close()
    return render_template('bin.html', bins=bins, columns=safe_columns)


@app.route('/taxonomy')
def home2():
    return render_template('index.html', content="taxonomy page")


@app.route('/kegg')
def kegg():
    ko_id = request.args.get('ko_id')
    bin_id = request.args.get('bin_id')

    conn = get_db_connection()
    cur = conn.cursor()
    kegg_entries = {}

    query = """
    SELECT k.ko_id, k.kegg_name, k.kegg_full_name, b.bin_name, be.go, be.ko, be.eggnog_desc
    FROM kegg k
    LEFT JOIN bin_extra_kegg bek ON k.id = bek.kegg_id
    LEFT JOIN bin_extra be ON bek.extra_id = be.id
    LEFT JOIN bin b ON be.bin_id = b.id
    """

    if ko_id:
        context = f"Affichage pour KEGG ID: {ko_id}"
        query += " WHERE k.ko_id = ?"
        cur.execute(query, (ko_id,))
    elif bin_id:
        context = f"Affichage pour Bin ID: {bin_id}"
        query += " WHERE b.id = ?"
        cur.execute(query, (bin_id,))
    else:
        context = "Affichage de tous les KEGG IDs"
        cur.execute(query)

    rows = cur.fetchall()
    for row in rows:
        ko_key = (row[0], row[1], row[2])  # KO ID, Name, Full Name
        if ko_key not in kegg_entries:
            kegg_entries[ko_key] = []
        go_terms = row[4].split(',') if row[4] else []
        kegg_entries[ko_key].append((row[3], go_terms, row[5], row[6]))  # Bin Name, GO (as list), KO, EggNOG Description

    cur.close()
    conn.close()
    return render_template('kegg.html', context=context, kegg_entries=kegg_entries.items())



@app.route('/map')
def show_maps():
    bin_id = request.values.get('bin_id')
    ko_id = request.values.get('ko_id')

    conn = get_db_connection()
    cur = conn.cursor()

    maps = {}
    if bin_id:
        context = f"Maps associés au bin_id {bin_id}"
        query = """
                SELECT m.map_number, m.pathway_name, k.ko_id, k.kegg_name
                FROM map m
                JOIN bin_map bm ON m.id = bm.map_id
                LEFT JOIN map_kegg mk ON m.id = mk.map_id
                LEFT JOIN kegg k ON mk.kegg_id = k.id
                WHERE bm.bin_id = ?
                """
        cur.execute(query, (bin_id,))
    elif ko_id:
        context = f"Maps contenant l'identifiant KEGG {ko_id}"
        query = """
                SELECT m.map_number, m.pathway_name, k.ko_id, k.kegg_name
                FROM map m
                JOIN map_kegg mk ON m.id = mk.map_id
                JOIN kegg k ON mk.kegg_id = k.id
                WHERE k.ko_id = ?
                """
        cur.execute(query, (ko_id,))
    else:
        context = "Tous les Maps"
        query = """
                SELECT m.map_number, m.pathway_name, k.ko_id, k.kegg_name
                FROM map m
                LEFT JOIN map_kegg mk ON m.id = mk.map_id
                LEFT JOIN kegg k ON mk.kegg_id = k.id
                """
        cur.execute(query)

    for row in cur.fetchall():
        map_key = (row[0], row[1])
        if map_key not in maps:
            maps[map_key] = []
        if row[2] and row[3]:  # Ensure ko_id and kegg_name are not None
            maps[map_key].append((row[2], row[3]))

    conn.close()

    return render_template('maps.html', maps=maps.items(), context=context)


@app.route('/bin')
def show_bins():
    show_taxonomy = request.args.get('show_taxonomy') == 'true'
    default_columns = ['bin.bin_name', 'bin.completeness', 'bin.contamination']
    taxonomy_columns = ['taxonomy._kingdom_', 'taxonomy._phylum_', 'taxonomy._class_', 'taxonomy._order_',
                        'taxonomy._family_', 'taxonomy._genus_', 'taxonomy._species_']

    display_columns = default_columns
    join_query = ""
    if show_taxonomy:
        display_columns += taxonomy_columns
        join_query = " LEFT JOIN taxonomy ON bin.taxonomic_id = taxonomy.id"

    conn = get_db_connection()
    cur = conn.cursor()
    query = f"SELECT {', '.join(display_columns)} FROM bin{join_query}"
    print(query)
    cur.execute(query)
    bins = cur.fetchall()
    conn.close()

    display_column_labels = [col.split('.')[1] if '.' in col else col for col in display_columns]

    return render_template('bin.html', bins=bins, columns=display_column_labels)


@app.route('/')
def home():
    return render_template('index.html', content="Testing")

if __name__ == '__main__':
    app.run(debug=True)
