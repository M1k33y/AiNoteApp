from db import *

print("Initializing DB…")
init_db()

print("Adding 2 topics…")
create_topic("Python", "Limbaj de programare.")
create_topic("Machine Learning", "Modele și algoritmi.")

print("Current topics:")
for t in get_topics():
    print(dict(t))

print("Adding notes to topic 1…")
create_note(1, "Variabile", "Ce este o variabilă în Python.")
create_note(1, "Liste", "Liste și operații.")

print("Notes in topic 1:")
for n in get_notes_by_topic(1):
    print(dict(n))