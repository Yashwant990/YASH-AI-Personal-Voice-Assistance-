import json
import pickle
import numpy as np 
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Embedding, GlobalAveragePooling1D
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.callbacks import EarlyStopping

# Ensure your intents.json is in the correct location (using relative path here)
with open("intents.json") as file:
    data = json.load(file)


training_sentences = []
training_labels = []
labels = []
responses = {}

for intent in data['intents']:
    for pattern in intent['patterns']:
        training_sentences.append(pattern)
        training_labels.append(intent['tag'])
    responses[intent['tag']] = intent['responses']

    if intent['tag'] not in labels:
        labels.append(intent['tag'])

number_of_classes = len(labels)
print("Number of classes:", number_of_classes)

# Encode labels
label_encoder = LabelEncoder()
label_encoder.fit(training_labels)
training_labels = label_encoder.transform(training_labels)

# Tokenizer
oov_token = "<OOV>"
tokenizer = Tokenizer(oov_token=oov_token)
tokenizer.fit_on_texts(training_sentences)
word_index = tokenizer.word_index
sequences = tokenizer.texts_to_sequences(training_sentences)
max_len = 20
padded_sequences = pad_sequences(sequences, truncating='post', maxlen=max_len)

# Dynamic vocab size
vocab_size = len(word_index) + 1

# --- ARCHITECTURE CHANGES TO INCREASE CONFIDENCE ---
embedding_dim = 32  # Increased from 16 to 32 (Richer word representation)

# Model
model = Sequential()
model.add(Embedding(vocab_size, embedding_dim, input_length=max_len))
model.add(GlobalAveragePooling1D())
model.add(Dense(64, activation="relu"))  # Increased from 16 to 64 (More learning capacity)
model.add(Dense(64, activation="relu"))  # Increased from 16 to 64
model.add(Dense(number_of_classes, activation="softmax"))

model.compile(loss='sparse_categorical_crossentropy', optimizer="adam", metrics=["accuracy"])
model.summary()

# --- TRAINING CONFIGURATION CHANGES ---
# Increased epochs to 500, but kept patience low (5) to restore the best weights efficiently.
es = EarlyStopping(monitor='loss', patience=5, restore_best_weights=True) 
history = model.fit(
    padded_sequences, 
    np.array(training_labels), 
    epochs=500, 
    callbacks=[es]
)

# Save model and preprocessors
model.save("chat_model.h5")

with open("tokenizer.pkl", "wb") as f:
    pickle.dump(tokenizer, f, protocol=pickle.HIGHEST_PROTOCOL)

with open("label_encoder.pkl", "wb") as encoder_file:
    pickle.dump(label_encoder, encoder_file, protocol=pickle.HIGHEST_PROTOCOL)

print("Model training complete. New model and pre-processors saved.")