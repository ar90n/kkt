import kkt_example

submission = kkt_example.load_sample_submission()
for _, row in submission.iterrows():
    row["Label"] = kkt_example.choice()

submission.to_csv("submission.csv")
