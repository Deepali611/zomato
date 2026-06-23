# Context: AI-Powered Restaurant Recommendation System

## Overview

This project aims to build an AI-powered restaurant recommendation service inspired by Zomato.  
The system should combine structured restaurant data with a Large Language Model (LLM) to deliver personalized, human-like restaurant recommendations.

## Core Objective

Design and implement an application that:

- Accepts user preferences (location, budget, cuisine, rating, and optional constraints)
- Uses a real-world Zomato restaurant dataset
- Uses an LLM to rank and explain recommendations
- Displays results in a clear and user-friendly format

## Dataset Context

- **Source:** [Hugging Face - ManikaSaini/zomato-restaurant-recommendation](https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation)
- **Expected extracted fields:**
  - Restaurant name
  - Location
  - Cuisine
  - Cost
  - Rating
  - Any other useful metadata available in dataset

## End-to-End Workflow

### 1) Data Ingestion

- Load the Zomato dataset from Hugging Face
- Preprocess and normalize relevant columns
- Keep only fields required for filtering and recommendation generation

### 2) User Input Collection

Collect the following user preferences:

- Location (example: Delhi, Bangalore)
- Budget tier (low, medium, high)
- Preferred cuisine (example: Italian, Chinese)
- Minimum acceptable rating
- Additional preferences (example: family-friendly, quick service)

### 3) Integration Layer

- Filter candidate restaurants based on user constraints
- Convert filtered structured records into prompt-ready context
- Design a prompt that enables LLM reasoning and ranking

### 4) Recommendation Engine (LLM)

Use the LLM to:

- Rank restaurant candidates
- Explain why each recommendation matches user preferences
- Optionally provide a short summary of the final shortlist

### 5) Output Display

Show top recommendations in a readable format including:

- Restaurant name
- Cuisine
- Rating
- Estimated cost
- AI-generated explanation

## Functional Expectations

- Recommendations should be personalized to user constraints
- Ranking logic should be transparent via explanations
- Final output should prioritize usability and clarity

## Prompting Requirements (LLM)

The prompt should:

- Receive structured restaurant candidates
- Consider user preferences as hard/soft constraints
- Return ranked recommendations with concise reasoning
- Avoid hallucinating fields not present in provided data

## Suggested Implementation Components

- **Data loader:** pulls and prepares Hugging Face dataset
- **Preference parser:** validates/normalizes user input
- **Filter module:** applies deterministic pre-LLM constraints
- **Prompt builder:** injects filtered records + user profile into prompt
- **LLM client:** obtains ranked, reasoned recommendations
- **Renderer/UI layer:** displays final recommendation cards/list

## Success Criteria

- User receives relevant recommendations aligned with preferences
- Each recommendation includes clear "why this fits" reasoning
- Output is concise, actionable, and easy to compare

