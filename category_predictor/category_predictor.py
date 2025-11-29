# category_predictor.py
import fasttext
import os
# the lines below is a patch from https://github.com/facebookresearch/fastText/issues/1067
fasttext.FastText.eprint = lambda x: None
MODEL_PATH = 'models/category_model.ftz'

class CategoryPredictor:
    def __init__(self):
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")
        try:
            print("model loading")
            self.model = fasttext.load_model(MODEL_PATH)
            print("model loaded")
        except Exception as e:
            raise RuntimeError(f"Failed to load fasttext model: {e}")

    def predict(self, merchant_name):
        try:
            #return "Household","misc"
            print("Start predicting")
            prediction = self.model.predict(merchant_name)
            print("End predicting")
            label = prediction[0][0]  # fasttext returns labels like __label__Category_Subcategory
            
            if label.startswith('__label__'):
                label = label[len('__label__'):]  # Remove the prefix
            
            # Assume labels are formatted as Category__Subcategory
            parts = label.split('__', 1)
            if len(parts) == 2:
                return parts[0].replace("_"," "), parts[1].replace("_"," ")
            else:
                return parts[0].replace("_"," "), ''  # If subcategory is not provided

        except Exception as e:
            print(f"Error predicting category: {e}")
            return 'Household', 'misc'  # Fallback category

# Example usage for quick test
#if __name__ == '__main__':
#    predictor = CategoryPredictor()
#    category, subcategory = predictor.predict("Avenue super mart")
#    print(f"Predicted Category: {category}, Subcategory: {subcategory}")
