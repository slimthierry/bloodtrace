/**
 * FHIR Patient resource builder.
 *
 * Maps BloodTrace Donor data to HL7 FHIR R4 Patient resources.
 * See: https://www.hl7.org/fhir/patient.html
 */

import type { Donor } from '../../types';

export interface FHIRPatient {
  resourceType: 'Patient';
  id: string;
  identifier: Array<{
    system: string;
    value: string;
  }>;
  name: Array<{
    family: string;
    given: string[];
    text?: string;
  }>;
  birthDate?: string;
  telecom?: Array<{
    system: string;
    value: string;
    use?: string;
  }>;
  extension?: Array<{
    url: string;
    valueCodeableConcept?: {
      coding: Array<{
        system: string;
        code: string;
        display: string;
      }>;
      text: string;
    };
  }>;
}

export function buildFHIRPatient(params: {
  id: string;
  ipp: string;
  firstName: string;
  lastName: string;
  birthDate?: string;
  bloodType?: string;
  rhFactor?: string;
  phone?: string;
  email?: string;
}): FHIRPatient {
  const telecom: FHIRPatient['telecom'] = [];
  if (params.phone) {
    telecom.push({ system: 'phone', value: params.phone, use: 'home' });
  }
  if (params.email) {
    telecom.push({ system: 'email', value: params.email, use: 'home' });
  }

  const extensions: FHIRPatient['extension'] = [];
  if (params.bloodType) {
    extensions.push({
      url: 'http://bloodtrace.local/fhir/StructureDefinition/blood-type',
      valueCodeableConcept: {
        coding: [{
          system: 'http://loinc.org',
          code: '882-1',
          display: `ABO group: ${params.bloodType}`,
        }],
        text: `${params.bloodType}${params.rhFactor || ''}`,
      },
    });
  }

  return {
    resourceType: 'Patient',
    id: params.id,
    identifier: [{
      system: 'http://bloodtrace.local/fhir/identifier/ipp',
      value: params.ipp,
    }],
    name: [{
      family: params.lastName,
      given: [params.firstName],
      text: `${params.firstName} ${params.lastName}`,
    }],
    birthDate: params.birthDate,
    telecom: telecom.length > 0 ? telecom : undefined,
    extension: extensions.length > 0 ? extensions : undefined,
  };
}

export function buildFHIRPatientFromDonor(donor: Donor): FHIRPatient {
  return buildFHIRPatient({
    id: String(donor.id),
    ipp: donor.ipp,
    firstName: donor.first_name,
    lastName: donor.last_name,
    birthDate: donor.date_of_birth,
    bloodType: donor.blood_type,
    rhFactor: donor.rh_factor,
    phone: donor.phone,
    email: donor.email,
  });
}
