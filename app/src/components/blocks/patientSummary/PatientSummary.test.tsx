import PatientSummary from "./PatientSummary"
import { render, screen } from "@testing-library/react"

describe("PatientSummary", () => {
  afterEach(() => {
    jest.clearAllMocks()
  })

  it("renders provided patient information", () => {
    const mockDetails = {
      birthDate: "date",
      familyName: "surname",
      givenName: ["otherName"],
      nhsNumber: "nhsNum",
      postalCode: "PC",
      superseded: false,
      restricted: false,
    }

    render(<PatientSummary patientDetails={mockDetails} />)

    expect(screen.getByText(mockDetails.birthDate)).toBeInTheDocument()
    expect(screen.getByText(mockDetails.familyName)).toBeInTheDocument()
    //expect(screen.getByText(mockDetails.givenName)).toBeInTheDocument()
  })
})
