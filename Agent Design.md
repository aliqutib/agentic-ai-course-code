1. **Goal**



Student have covered all topics found in created study plan, which was made according to the topic which was required to cover, by passing all relevant assessment with sufficient score



**2. Observation / Context**



The overall topic and content to cover

The depth and level of topic given by student or found in the study material

The position of the topic in outline / study plan agent created in initial steps

Available permitted access to study material

Current topic

Student's responses, answers, quiz scores, and topic progress

Weightage of the topic in completing overall goal



**3. Tools / Action**



A - generate\_current\_content\_to\_study()

B - access\_study\_material()

C - create\_study\_plan()

D - move\_forward\_in\_plan()

E - map\_notes\_with\_quries()

F - create\_quiz()

G - analyze\_performance()

H - review\_progress()

I - analyze\_depth\_of\_content()

J - search\_web()





**4. Decision Making**





Student say "Help me prepare for my deep learning exam for ANN and CNN architecture"

LLM examines context -> there are two different topics

Choose tool B

tool returns material related to these two topic

LLM choose tool I

tool returns depth of content

LLM choose tool C

tool returns concrete road maps to preparing according to accessed study material

LLM choose tool A

tool returns tailored content of first topic in road map

if user ask any query after reading it

LLM choose E

tool return notes backed answer to student

If user prompt for quiz

LLM choose F

tool returns structured quiz up to covered content

after quiz is done

LLM choose G

tool returns quiz score and feedback

If user prompt to move to next topic in study plan

LLM choose H

tool returns progress done so far

LLM choose D

tool returns next topic needed to be covered 



**5. State**



**Short-term State**

current topic

mapped notes with queries

The depth and level of topic



**Long term State**

progress for preparation

cumulative and individual quiz score

study plan



**6. Termination**



1. Study plan created was completed with all quizzes done
2. User explicitly asked for break
3. Progression bar hit 100%



**7. Failure / Recovery**



F: No study material was found related to asked topic

R: Ask for permission of another folder (if material is there) or search the web for the content



F: User asked for two different unrelated topics (ANN and Agile Manifesto)

R: Response user to select one flow or call tool C separately for both



F: Asked query wasn't find in the accessed notes/material

R: Ask user to give response form web\_search



