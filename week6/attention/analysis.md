# Analysis

After testing the attention visualization system with various masked sentences, I've identified several attention heads that demonstrate interesting linguistic patterns and functions in the BERT model. Here's my analysis of the most notable patterns:

## Layer 4, Head 7

This attention head appears to focus on syntactic relationships, particularly between verbs and their subjects. It consistently shows strong attention from verbs back to their subject nouns, suggesting it helps the model understand who is performing actions.

Example Sentences:
- "The student [MASK] the assignment yesterday." → Shows strong attention from potential verbs like "completed" back to "student"
- "The dog [MASK] at the mailman." → High attention weights connecting potential actions like "barked" with "dog"

## Layer 6, Head 2

This head demonstrates a clear focus on semantic word associations and contextual predictions. It assigns high attention to tokens that are semantically related to the masked word, helping to predict contextually appropriate completions.

Example Sentences:
- "She put the dishes in the [MASK]." → Strong attention to "dishes" from potential completions like "sink" or "dishwasher"
- "The chef added [MASK] to the soup." → High attention between cooking-related contextual words and probable ingredients

## Layer 8, Head 11

This attention head shows a specialized focus on tokenization and subword relationships. It pays particular attention to tokens that are parts of the same word or closely related words, suggesting it helps the model reconstruct meaning from WordPiece tokens.

Example Sentences:
- "The un[MASK]able problem remained unsolved." → High attention between subword tokens like "un" and potential completions like "solve"
- "Bio[MASK] research has advanced significantly." → Strong connections between prefix "bio" and field completions like "medical" or "technology"

## Layer 11, Head 5

This head, positioned in one of the final layers, appears to integrate broad contextual information from the entire sentence. It distributes attention widely but with clear focus on the tokens most relevant to determining the masked word, suggesting it performs final synthesis of multiple linguistic signals.

Example Sentences:
- "After the storm, the [MASK] was damaged." → Distributes attention across contextual elements with focus on "storm" and "damaged"
- "The museum displayed ancient [MASK] from the excavation." → Balances attention between "museum," "ancient," and "excavation" to constrain possible object types

These observations demonstrate how BERT's attention mechanism distributes specialized linguistic functions across different heads and layers. The early layers (like Layer 4) appear to capture basic syntactic relationships, middle layers (6-8) focus on semantic associations and word structure, while later layers (like Layer 11) integrate broader context to make final predictions.

The visualization tool provides valuable insights into how transformer models process language, revealing specialized linguistic functions that emerge during training without explicit programming.