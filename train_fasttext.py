import fasttext

# Train the classifier
model = fasttext.train_supervised(
    input='data/training_data.txt',
    epoch=25,
    lr=1.0,
    wordNgrams=2,
    verbose=2,
    minCount=1
)

# Save the model
model.save_model('models/category_model.ftz')

print("Model training completed and saved!")
