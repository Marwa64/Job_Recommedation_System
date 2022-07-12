import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from jobs_scraper import JobsScraper
from pathlib import Path
import random


# Scrap indeed for jobs related to the track
def scrapping(track):
  path_to_file = "C:/Users\mrawa/PycharmProjects/Jobs Recommedation System/" + track + ".csv"
  path = Path(path_to_file)
  if path.is_file():
    df = pd.read_csv(path_to_file)
  else:
    scraper = JobsScraper(country="us", position=track, location="remote", pages=7, full_urls=True)
    df = scraper.scrape()
    df.to_csv(path_to_file)

  return df


def job_recommendation(track, payload, number_of_recommendations):
  df = scrapping(track)

  # Create a series with the url as the key since it's unique
  indices = pd.Series(df.index, index=df['url'])

  if payload.__len__() > 0:
    # Add the job we want to get similar jobs for to the data frame
    for viewed_job in payload:
      try:
        print(indices[viewed_job['url']])
      except:
        job_to_compare = pd.DataFrame({
          'title': [viewed_job['title']],
          'location': [viewed_job['location']],
          'company': [viewed_job['company']],
          'summary': [viewed_job['summary']],
          'salary': [viewed_job['salary']],
          'url': [viewed_job['url']]
        })
        df = df.append(job_to_compare, ignore_index=True)

  # Converting text to vector
  tf = TfidfVectorizer(analyzer='word', ngram_range=(1, 3), min_df=0, stop_words='english')
  matrix = tf.fit_transform(df['summary'])

  # Calculate the cosine similarities based on the job summaries
  cosine_similarities = cosine_similarity(matrix,matrix)

  # Create a series with the url as the key since it's unique
  indices = pd.Series(df.index, index=df['url'])

  # Get recommendations
  recommendations = []
  if payload.__len__() > 0:
    for viewed_job in payload:
      idx = indices[viewed_job['url']]
      sim_scores = list(enumerate(cosine_similarities[idx]))
      sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
      sim_scores = sim_scores[1:31]
      job_indices = [i[0] for i in sim_scores]
      recommendation = df.iloc[job_indices].head(round(number_of_recommendations / payload.__len__()))
      recommendations.append(recommendation)

  else:
    number_of_jobs = indices.__len__() - 1
    for x in range(11):
      idx = indices[random.randint(0, number_of_jobs)]
      sim_scores = list(enumerate(cosine_similarities[idx]))
      sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
      sim_scores = sim_scores[1:31]
      job_indices = [i[0] for i in sim_scores]
      recommendation = df.iloc[job_indices].head(1)
      recommendations.append(recommendation)

  return recommendations
