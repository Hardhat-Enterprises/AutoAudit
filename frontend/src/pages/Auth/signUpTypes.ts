export interface SignUpFormData {
  firstName: string;
  lastName: string;
  email: string;
  organizationName: string;
  password: string;
  confirmPassword: string;
}

export interface SignUpSubmitPayload extends SignUpFormData {
  agreeTerms: boolean;
}
