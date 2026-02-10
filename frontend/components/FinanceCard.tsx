export default function FinanceCard() {
    return (
      <div className="card">
        <h2>Financing Estimates</h2>
        <p>
          Monthly payments are calculated using simple interest.
          Loan term is based on COE remaining minus a 4-month buffer.
        </p>
        
        <div className="finance-table-wrapper">
          <table className="finance-table">
            <thead>
              <tr>
                <th>Downpayment</th>
                <th>Interest Rate</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>$0</td>
                <td>4.98%</td>
              </tr>
              <tr>
                <td>$10,000</td>
                <td>4.00%</td>
              </tr>
              <tr>
                <td>$20,000</td>
                <td>3.50%</td>
              </tr>
              <tr>
                <td>$30,000</td>
                <td>3.50%</td>
              </tr>
              <tr>
                <td>$40,000</td>
                <td>3.00%</td>
              </tr>
              <tr>
                <td>$50,000</td>
                <td>3.00%</td>
              </tr>
            </tbody>
          </table>
        </div>
        

        <p className="disclaimer">
          These are estimates only. Actual rates and terms vary by lender.
        </p>
      </div>
    );
  }