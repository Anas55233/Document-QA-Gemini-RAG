from rag import answer_question, load_vector_store, get_all_chunks, build_bm25_index

def run_evaluation(test_cases, vector_store, bm25, all_chunks):
    results = []

    for case in test_cases:
        question = case["question"]
        expected_keywords = case["expected_keywords"]

        response = answer_question(
            question,
            chat_history="",
            vector_store=vector_store,
            bm25=bm25,
            all_chunks=all_chunks
        )

        answer = response["answer"]

        # Simple check: did the answer contain the expected keyword(s)?
        passed = all(keyword.lower() in answer.lower() for keyword in expected_keywords)

        results.append({
            "question": question,
            "answer": answer,
            "expected_keywords": expected_keywords,
            "passed": passed
        })

    return results



test_cases = [
    {
        "question": "date range of statement",
        "expected_keywords": ["22 Dec 2025", "05 Jun 2026"]
    },
    {
        "question": "on 13 dec 2025, what was transferred?",
        "expected_keywords": ["MUHAMMAD AWAIS", "AYAZ"]
    },
    {
        "question": "from ALTAFHUSSAIN, how much and on which date money received",
        "expected_keywords": ["07 Jan 2026", "32,000"]
    },
     {
        "question": "on 14 jan 2026, what was available balance?",
        "expected_keywords": ["Available Balance", "PKR 411,424.39"]
    },
      {
        "question": "on which dates, cash has been withdrawl?",
        "expected_keywords": ["ATM Cash Withdrawal", "22 Dec 2025", "06 Jan 2026"]
    }
]


if __name__ == "__main__":
    vector_store = load_vector_store()
    all_chunks = get_all_chunks(vector_store)
    bm25 = build_bm25_index(all_chunks)

    results = run_evaluation(test_cases, vector_store, bm25, all_chunks)

    passed_count = sum(1 for r in results if r["passed"])

    print(f"\n=== EVALUATION REPORT ===")
    print(f"Passed: {passed_count}/{len(results)}\n")

    for r in results:
        status = "✅ PASS" if r["passed"] else "❌ FAIL"
        print(f"{status} — {r['question']}")
        if not r["passed"]:
            print(f"   Expected keywords: {r['expected_keywords']}")
            print(f"   Got answer: {r['answer'][:200]}")
        print()